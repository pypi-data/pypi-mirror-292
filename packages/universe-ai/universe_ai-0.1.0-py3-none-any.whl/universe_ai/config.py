from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import Optional


load_dotenv()


class Config(BaseModel):

    class Proxy(BaseModel):
        http: str = os.getenv('HTTP_PROXY', '')
        https: str = os.getenv('HTTPS_PROXY', '')

    proxy: Proxy = Proxy()
    timeout: Optional[int] = int(os.getenv('TIME_OUT', 60))


def get_config() -> Config:
    return Config()
