from dotenv import load_dotenv
import os
from universe_ai.config import Config as BaseConfig
from pydantic import BaseModel
from typing import Optional

load_dotenv()


class Config(BaseConfig):
    class Auth(BaseModel):
        cookie: str = os.getenv('MONICA_COOKIE', '')

    class Chat(BaseModel):
        chat_model: str = os.getenv('MONICA_MODEL', 'gpt-4')

    auth: Auth = Auth()
    chat: Chat = Chat()


def get_config() -> Config:
    return Config()
