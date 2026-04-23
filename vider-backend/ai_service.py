"""
VIDER AI Service — Local LLM inference via HuggingFace Transformers + PyTorch.

Model  : Qwen/Qwen2.5-1.5B-Instruct  (configurable via LLM_MODEL env)
Device : CUDA (auto) when available, else CPU
Dtype  : bfloat16 on CUDA, float32 on CPU
"""

import os
import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — defines VIDER's personality
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "Bạn là VIDER, một trợ lý AI thông minh, thân thiện và chuyên nghiệp. "
    "Hãy trả lời bằng tiếng Việt trừ khi người dùng yêu cầu ngôn ngữ khác. "
    "Trả lời ngắn gọn, chính xác và hữu ích."
)


class LocalLLM:
    """Lightweight local LLM wrapper.

    Key design decisions
    --------------------
    * Uses ``model.generate()`` directly instead of ``pipeline`` to avoid
      the device‑conflict that occurs when ``device_map="auto"`` distributes
      the model across devices while ``pipeline(device=0)`` expects a single
      device.
    * Applies the model's **chat template** (``tokenizer.apply_chat_template``)
      so Instruct-tuned models (Qwen, Phi, …) produce high‑quality output.
    * Model is loaded **lazily** on first call to ``generate_response()``,
      not at import time, so the server starts instantly.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv(
            "LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct"
        )
        self.has_cuda = torch.cuda.is_available()
        self.torch_dtype = torch.bfloat16 if self.has_cuda else torch.float32
        self.device = "cuda" if self.has_cuda else "cpu"

        # Lazy — populated by _load_model()
        self._tokenizer = None
        self._model = None
        self._loaded = False

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------
    def _load_model(self):
        if self._loaded:
            return

        logger.info("Loading model '%s' (dtype=%s, device=%s) …",
                     self.model_name, self.torch_dtype, self.device)

        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True,
            trust_remote_code=True,
        )

        # Ensure pad_token exists (some models omit it)
        if self._tokenizer.pad_token is None:
            self._tokenizer.pad_token = self._tokenizer.eos_token

        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            dtype=self.torch_dtype,
            trust_remote_code=True,
        ).to(self.device)
        self._model.eval()

        logger.info("Model loaded successfully.")
        self._loaded = True

    # ------------------------------------------------------------------
    # Chat‑template prompt builder
    # ------------------------------------------------------------------
    def _build_messages(self, chat_history: list[dict]) -> list[dict]:
        """Convert raw chat_history to the messages list expected by the
        chat template, prepending the system prompt."""
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in chat_history:
            role = msg.get("role", "user")
            # Normalise role names — the frontend uses "bot" while the
            # model expects "assistant".
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
            Nucleus‑sampling probability mass.

        Returns
        -------
        str
            The assistant's reply text.
        """
        # Lazy load
        if not self._loaded:
            self._load_model()

        messages = self._build_messages(chat_history)

        # Use the tokenizer's built-in chat template (works for Qwen, Phi, …)
        tokenized = self._tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
        )

        # Newer transformers return a BatchEncoding; older ones return a tensor.
        if hasattr(tokenized, "input_ids"):
            input_ids = tokenized["input_ids"].to(self._model.device)
        else:
            input_ids = tokenized.to(self._model.device)

        # Generate
        with torch.no_grad():
            output_ids = self._model.generate(
                input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature if temperature > 0 else None,
                top_p=top_p if temperature > 0 else None,
                pad_token_id=self._tokenizer.pad_token_id,
            )

        # Decode only the *new* tokens (strip the prompt)
        new_tokens = output_ids[0, input_ids.shape[1]:]
        reply = self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

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
