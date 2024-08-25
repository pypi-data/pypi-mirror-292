from pydantic import BaseModel
from typing import Optional, Literal


class Message(BaseModel):
    content: str
    type: Literal["text", "image", "video", "audio", "file", "location", "contact"] = "text"
    role: Literal["user", "bot"] = "user"


class MessageChain(BaseModel):
    messages: list[Message]


class ModelResponse(BaseModel):
    success: bool = True
    message: str = ""
    content: str = ""
