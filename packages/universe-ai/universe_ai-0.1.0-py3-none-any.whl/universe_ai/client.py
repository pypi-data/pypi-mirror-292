from .model import MessageChain, ModelResponse
from abc import abstractmethod
from typing import Tuple, AsyncIterator, Union


class BaseClient:
    def __init__(self):
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def chat(self, message_chain: MessageChain, stream: bool, *args, **kwargs) -> Union[AsyncIterator[ModelResponse], ModelResponse]:
        pass

    @abstractmethod
    async def add_system_prompt(self, message):
        pass


