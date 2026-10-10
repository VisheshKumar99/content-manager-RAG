
import os

from rag.llm.base import BaseLLM
from rag.llm.openAI import OpenAILLM
from rag.llm.ollama import OllamaLLM


def get_llm(provider: str | None = None) -> BaseLLM:
    provider = (
        provider or os.getenv("LLM_PROVIDER", "ollama")
    ).lower()

    providers = {
        "openai": OpenAILLM,
        "ollama": OllamaLLM,
    }

    llm_class = providers.get(provider)

    if llm_class is None:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    return llm_class()