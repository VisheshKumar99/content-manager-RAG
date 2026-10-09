"""The RAG agent: retrieves context, then answers with the LLM."""

from openai import OpenAI

from rag.retriever import Retriever

client = OpenAI()

CHAT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = (
    "You are a content manager assistant. Answer using the provided context. "
    "If the context is not enough, say so."
)


class Agent:
    def __init__(self) -> None:
        self.retriever = Retriever()

    def run(self, message: str) -> str:
        """Retrieve context for the message and return the LLM's answer."""
        context = self.retriever.search(message)
        context_block = "\n\n".join(context) if context else "(no context yet)"

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context_block}\n\nQuestion: {message}",
                },
            ],
        )
        return response.choices[0].message.content or ""
