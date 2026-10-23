from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.core.limiter import limiter
from app.services.chat_service import ChatLimitReached, generate_reply

router = APIRouter(tags=["Chat"])


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatMessage(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(request: Request, payload: ChatMessage):
    try:
        reply = await generate_reply(payload.message.strip(), [t.model_dump() for t in payload.history])
    except ChatLimitReached:
        raise HTTPException(status_code=429, detail="Hira has reached today's chat limit. Please try again tomorrow.")
    return {"reply": reply}
