
import os
from openai import OpenAI
from rag.llm.base import BaseLLM


class OllamaLLM(BaseLLM):

    def __init__(self):
        self.client = OpenAI(
            base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434/v1"
            ),
            api_key="ollama",
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "300")),
        )
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content or ""