import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class LocalLLM:
    """Lightweight local LLM wrapper using HuggingFace Transformers + PyTorch.

    - Default model: 'microsoft/Phi-3-mini-4k-instruct' (small, demo-friendly).
    - Uses device_map="auto" and torch_dtype=torch.bfloat16 when CUDA is available.
    - Provides generate_response(chat_history) which accepts a list of messages:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("LLM_MODEL", "microsoft/Phi-3-mini-4k-instruct")

        self.has_cuda = torch.cuda.is_available()
        # prefer bfloat16 when CUDA + support exists, else fallback to float16 on CUDA or float32 on CPU
        if self.has_cuda:
            try:
                dtype = torch.bfloat16
            except Exception:
                dtype = torch.float16
        else:
            dtype = torch.float32

        self.torch_dtype = dtype

        # Lazy load model components
        self.tokenizer = None
        self.model = None
        self.generator = None

        self._load_model()

    def _load_model(self):
        # Use device_map="auto" to let accelerate/hf dispatch to available devices
        device_map = "auto"

        # load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)

        # load model (may take time and disk space)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=device_map,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
        )

        # create a simple text-generation pipeline for convenience
        device = 0 if self.has_cuda else -1
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=device,
            # disable default truncation so we control prompt length
            # (note: some tokenizers/models may behave differently)
        )

    def _build_prompt(self, chat_history: list[dict]) -> str:
        # Simple role-prefixed prompt. You can replace this with a more advanced system prompt.
        parts = []
        for msg in chat_history:
            role = msg.get("role", "user")
            content = msg.get("content", "").strip()
            if role == "user":
                parts.append(f"User: {content}")
            else:
                parts.append(f"Assistant: {content}")
        parts.append("Assistant:")
        return "\n".join(parts)

    def generate_response(self, chat_history: list[dict], max_new_tokens: int = 256, temperature: float = 0.2) -> str:
        """Generate a single assistant reply from chat_history.

        Returns the assistant text (str).
        """
        if self.generator is None:
            self._load_model()

        prompt = self._build_prompt(chat_history)

        # Call the pipeline to generate text
        outputs = self.generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=temperature,
            top_p=0.95,
            num_return_sequences=1,
        )

        text = outputs[0]["generated_text"]

        # Remove the prompt prefix if present, and any leading role label
        if prompt and text.startswith(prompt):
            text = text[len(prompt):]
        text = text.strip()
        if text.startswith("Assistant:"):
            text = text[len("Assistant:"):].strip()

        return text


# Convenience singleton for quick use in the API
llm = LocalLLM()
