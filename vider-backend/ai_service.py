"""
VIDER AI Service — Local LLM + Tavily Web Search.

Model  : Qwen2.5-3B-Instruct-GGUF  Q4_K_M  (configurable via env vars)
Engine : llama.cpp  — optimised C/C++ inference, runs great on CPU
Search : Tavily API — AI-optimised web search (1,000 free searches/month)

Flow when user asks a question
-------------------------------
1. Model receives the question with a system prompt that explains how to
   request a web search using ``[SEARCH]query[/SEARCH]`` tags.
2. If the model's first reply contains a search tag, we:
   a. Extract the query.
   b. Call the Tavily API.
   c. Inject the search results back into the conversation.
   d. Ask the model to answer again with the new context.
3. If no search tag is found, the reply is returned as-is.
"""

import os
import re
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Search tag pattern — the model emits [SEARCH]…[/SEARCH] when it needs data
# ---------------------------------------------------------------------------
SEARCH_PATTERN = re.compile(r"\[SEARCH\](.*?)\[/SEARCH\]", re.DOTALL)

# ---------------------------------------------------------------------------
# System prompt — instructs the model on how & when to search
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "Bạn là VIDER, một trợ lý AI thông minh, thân thiện và chuyên nghiệp. "
    "Hãy trả lời bằng tiếng Việt trừ khi người dùng yêu cầu ngôn ngữ khác. "
    "Trả lời ngắn gọn, chính xác và hữu ích. "
    "Nếu bạn không biết câu trả lời, hãy nói thật, tuyệt đối không được bịa.\n\n"
    "BẠN CÓ KHẢ NĂNG TÌM KIẾM WEB. "
    "Khi câu hỏi cần thông tin thời gian thực hoặc bạn không chắc chắn về câu trả lời "
    "(tin tức, thời tiết, giá cả, sự kiện, kiến thức chuyên sâu, v.v.), "
    "hãy trả lời ĐÚNG theo định dạng sau và KHÔNG thêm bất kỳ text nào khác:\n"
    "[SEARCH]từ khóa tìm kiếm bằng tiếng Anh hoặc tiếng Việt[/SEARCH]\n\n"
    "Ví dụ:\n"
    "- Người dùng hỏi: 'Thời tiết Hà Nội hôm nay?' → Bạn trả lời: [SEARCH]weather Hanoi today[/SEARCH]\n"
    "- Người dùng hỏi: 'Tỉ giá USD VNĐ?' → Bạn trả lời: [SEARCH]USD to VND exchange rate today[/SEARCH]\n"
    "- Người dùng hỏi: 'Xin chào' → Bạn trả lời bình thường, KHÔNG cần search.\n\n"
    "Chỉ dùng [SEARCH] khi THỰC SỰ cần thông tin bên ngoài. "
    "Các câu hỏi chào hỏi, toán học, lập trình, kiến thức phổ thông thì trả lời trực tiếp."
)


# ---------------------------------------------------------------------------
# Tavily Web Search
# ---------------------------------------------------------------------------
class WebSearcher:
    """Thin wrapper around the Tavily API."""

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.getenv("TAVILY_API_KEY", "")
            if not api_key:
                logger.warning(
                    "TAVILY_API_KEY not set — web search is disabled. "
                    "Get a free key at https://tavily.com"
                )
                return None
            from tavily import TavilyClient
            self._client = TavilyClient(api_key=api_key)
        return self._client

    def search(self, query: str, max_results: int = 5) -> str:
        """Run a web search and return a formatted text block for the LLM."""
        client = self._get_client()
        if client is None:
            return "(Web search is unavailable — TAVILY_API_KEY is not configured.)"

        try:
            logger.info("🔍 Tavily search: %s", query)
            response = client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_answer=True,
            )

            # Build a concise context block for the model
            parts: list[str] = []

            # Tavily's AI-generated answer (if available)
            if response.get("answer"):
                parts.append(f"📋 Tóm tắt: {response['answer']}")

            # Individual results
            for i, result in enumerate(response.get("results", []), 1):
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                parts.append(f"\n[{i}] {title}\n{content}\nNguồn: {url}")

            return "\n".join(parts) if parts else "(Không tìm thấy kết quả.)"

        except Exception as exc:
            logger.exception("Tavily search failed")
            return f"(Lỗi tìm kiếm: {exc})"


# ---------------------------------------------------------------------------
# Global searcher instance
# ---------------------------------------------------------------------------
web_searcher = WebSearcher()


# ---------------------------------------------------------------------------
# Local LLM (llama.cpp)
# ---------------------------------------------------------------------------
class LocalLLM:
    """llama.cpp–backed LLM wrapper with integrated web search."""

    def __init__(
        self,
        repo_id: str | None = None,
        filename: str | None = None,
    ):
        self.repo_id = repo_id or os.getenv(
            "LLM_REPO", "Qwen/Qwen2.5-3B-Instruct-GGUF"
        )
        self.filename = filename or os.getenv(
            "LLM_FILE", "qwen2.5-3b-instruct-q4_k_m.gguf"
        )
        self.n_ctx = int(os.getenv("LLM_CTX", "4096"))

        # Lazy — populated by _load_model()
        self._model = None
        self._loaded = False

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------
    def _load_model(self):
        if self._loaded:
            return

        from llama_cpp import Llama

        n_threads = os.cpu_count() or 4
        logger.info(
            "Loading GGUF model repo='%s' file='%s' (n_ctx=%d, threads=%d) …",
            self.repo_id, self.filename, self.n_ctx, n_threads,
        )

        self._model = Llama.from_pretrained(
            repo_id=self.repo_id,
            filename=self.filename,
            n_ctx=self.n_ctx,
            n_threads=n_threads,
            verbose=False,
        )

        logger.info("GGUF model loaded successfully.")
        self._loaded = True

    # ------------------------------------------------------------------
    # Message builder
    # ------------------------------------------------------------------
    def _build_messages(self, chat_history: list[dict]) -> list[dict]:
        """Prepend the system prompt to the raw chat history."""
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in chat_history:
            role = msg.get("role", "user")
            if role not in ("user", "assistant", "system"):
                role = "assistant"
            messages.append({"role": role, "content": msg.get("content", "")})

        return messages

    # ------------------------------------------------------------------
    # Single LLM call
    # ------------------------------------------------------------------
    def _call_llm(
        self,
        messages: list[dict],
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        response = self._model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return response["choices"][0]["message"]["content"].strip()

    # ------------------------------------------------------------------
    # Generation (with automatic web search)
    # ------------------------------------------------------------------
    def generate_response(
        self,
        chat_history: list[dict],
        max_new_tokens: int = 512,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ) -> str:
        """Generate an assistant reply, automatically searching the web
        if the model decides it needs external information.

        Two-pass flow
        -------------
        Pass 1: Model reads the conversation and either answers directly
                or emits ``[SEARCH]query[/SEARCH]``.
        Pass 2: (only if search was triggered) Model receives the search
                results and produces the final answer.
        """
        # Lazy load
        if not self._loaded:
            self._load_model()

        messages = self._build_messages(chat_history)

        # --- Pass 1: initial generation ---
        reply = self._call_llm(messages, max_new_tokens, temperature, top_p)
        logger.info("Pass 1 reply: %s", reply[:200])

        # --- Check for search request ---
        match = SEARCH_PATTERN.search(reply)
        if not match:
            # No search needed — return as-is
            return reply

        search_query = match.group(1).strip()
        if not search_query:
            return reply

        # --- Execute web search ---
        search_results = web_searcher.search(search_query)
        logger.info("Search results length: %d chars", len(search_results))

        # --- Pass 2: answer with search context ---
        # Append the search interaction to the conversation
        messages.append({"role": "assistant", "content": reply})
        messages.append({
            "role": "user",
            "content": (
                f"Dưới đây là kết quả tìm kiếm web cho '{search_query}':\n\n"
                f"{search_results}\n\n"
                "Dựa trên kết quả trên, hãy trả lời câu hỏi ban đầu của tôi "
                "một cách ngắn gọn, chính xác và dễ hiểu bằng tiếng Việt. "
                "Ghi rõ nguồn nếu cần."
            ),
        })

        final_reply = self._call_llm(messages, max_new_tokens, temperature, top_p)
        logger.info("Pass 2 reply: %s", final_reply[:200])

        return final_reply


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
llm: LocalLLM | None = None


def get_llm() -> LocalLLM:
    """Return the global LLM singleton, creating it if needed."""
    global llm
    if llm is None:
        llm = LocalLLM()
    return llm
