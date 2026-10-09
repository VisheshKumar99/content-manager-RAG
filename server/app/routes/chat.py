"""Chat endpoint that routes requests through the RAG agent."""

from fastapi import APIRouter
from pydantic import BaseModel

from rag.agent import Agent

router = APIRouter(prefix="/chat", tags=["chat"])
agent = Agent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = agent.run(request.message)
    return ChatResponse(answer=answer)
