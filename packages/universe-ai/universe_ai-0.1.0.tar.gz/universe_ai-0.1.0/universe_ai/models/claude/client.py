from typing import Union, AsyncIterator

from universe_ai.client import BaseClient
from universe_ai.model import ModelResponse, MessageChain
import anthropic
from .config import get_config


class ClaudeClient(BaseClient):
    @property
    def name(self):
        return "claude"

    def __init__(self):
        super().__init__()
        self.config = get_config()
        if not self.config.anthropic_api_key or self.config.anthropic_api_key == "":
            raise ValueError("ANTHROPIC_API_KEY is not set")
        if not self.config.claude_model or self.config.claude_model == "":
            raise ValueError("CLAUDE_MODEL is not set")
        self.client = anthropic.AsyncClient(
            api_key=self.config.anthropic_api_key,
        )
        self.system_prompt = ""

    def chat(self, message_chain: MessageChain, stream: bool, *args, **kwargs) -> Union[AsyncIterator[ModelResponse], ModelResponse]:
        return self.async_chat(message_chain, stream)

    async def async_chat(self, message_chain: MessageChain, stream: bool) -> AsyncIterator[ModelResponse]:
        messages = []
        for msg in message_chain.messages:
            if msg.type == 'text':
                messages.append({
                    "role": "user",
                    "content": msg.content
                })

        stream = await self.client.messages.create(
            system=self.system_prompt,
            max_tokens=8192,
            messages=messages,
            model=self.config.claude_model,
            stream=True,
        )

        async for response in stream:
            message_type = response.type
            # print(message_type)
            if message_type == "content_block_delta":
                message = response.delta.text
            else:
                message = ""

            yield ModelResponse(
                success=True,
                message="",
                content=message,
            )

    async def add_system_prompt(self, message):
        self.system_prompt = message
