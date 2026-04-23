"""
VIDER AI Service — Local LLM inference via llama-cpp-python (GGUF models).

Model  : Qwen2.5-3B-Instruct-GGUF  Q4_K_M  (configurable via env vars)
Engine : llama.cpp  — optimised C/C++ inference, runs great on CPU
RAM    : ~2 GB  (vs ~6 GB for the same model in float32 via Transformers)
"""

import os
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — defines VIDER's personality
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "Bạn là VIDER, một trợ lý AI thông minh, thân thiện và chuyên nghiệp. "
    "Hãy trả lời bằng tiếng Việt trừ khi người dùng yêu cầu ngôn ngữ khác. "
    "Trả lời ngắn gọn, chính xác và hữu ích. "
    "Nếu bạn không biết câu trả lời, hãy nói thật, tuyệt đối không được bịa."
)


class LocalLLM:
    """llama.cpp–backed LLM wrapper.

    Key advantages over the old Transformers backend
    -------------------------------------------------
    * Uses **GGUF** quantised weights (4-bit) — dramatically lower RAM.
    * Pure C/C++ inference — faster on CPU than PyTorch.
    * Built-in chat-template support via ``create_chat_completion()``.
    * Model is downloaded and cached automatically from HuggingFace Hub.
    """

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
    # Chat-template prompt builder
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
    # Generation
    # ------------------------------------------------------------------
    def generate_response(
        self,
        chat_history: list[dict],
        max_new_tokens: int = 512,
        temperature: float = 0.1,
        top_p: float = 0.9,
    ) -> str:
        """Generate an assistant reply from *chat_history*.

        Parameters
        ----------
        chat_history : list[dict]
            ``[{"role": "user"|"assistant", "content": "…"}, …]``
        max_new_tokens : int
            Maximum number of new tokens to generate.
        temperature : float
            Sampling temperature (0 = greedy).
        top_p : float
            Nucleus-sampling probability mass.

        Returns
        -------
        str
            The assistant's reply text.
        """
        # Lazy load
        if not self._loaded:
            self._load_model()

        messages = self._build_messages(chat_history)

        # llama-cpp-python handles chat templates internally
        response = self._model.create_chat_completion(
            messages=messages,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        reply = response["choices"][0]["message"]["content"].strip()
        return reply


# ---------------------------------------------------------------------------
# Singleton — the model is NOT loaded here; it loads lazily on first call.
# ---------------------------------------------------------------------------
llm: LocalLLM | None = None


def get_llm() -> LocalLLM:
    """Return the global LLM singleton, creating it if needed."""
    global llm
    if llm is None:
        llm = LocalLLM()
    return llm
