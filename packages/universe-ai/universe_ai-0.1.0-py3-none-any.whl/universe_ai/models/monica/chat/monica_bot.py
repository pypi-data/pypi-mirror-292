from typing import AsyncIterator, Optional, Tuple

from universe_ai.client import BaseClient
from universe_ai.model import ModelResponse
from universe_ai.model import MessageChain, ModelResponse, Message
from ..config import get_config, Config
from httpx import AsyncClient
import json
from .model import ChatRequestBody, Item, Data1, Data
from .base_model import BaseChatPostBody, BaseItem, BaseData, BaseData1
import uuid
from typing import Literal, Optional


def get_uuid() -> str:
    return str(uuid.uuid4()).lower()


def get_msg_id() -> str:
    return f"msg:{get_uuid()}"


def get_conv_id() -> str:
    return f"conv:{get_uuid()}"


def get_task_id() -> str:
    return f"task:{get_uuid()}"


class MonicaClient(BaseClient):
    @property
    def name(self):
        return "monica"

    async def add_system_prompt(self, message: str):
        self.system_prompt = message
        if message in self.chkpt_dict:
            self.load_checkpoint(message)
            return
        self.load_checkpoint("_internal_start_up")
        stream = self.chat(MessageChain(messages=[Message(type="text", content=message)]), is_advanced=False, is_continue=True)
        async for response in stream:
            pass
        self.save_checkpoint(message)

    def __init__(self, conv_id: Optional[str] = None):
        super().__init__()
        self.config: Config = get_config()
        self.client = self.get_client()
        if conv_id is None:
            self.conv_id = get_conv_id()

        self.conv_dict = {
            self.conv_id: {
                "parent_item_id": get_msg_id(),
                "pre_generated_reply_id": get_msg_id(),
                "parent_content": "__RENDER_BOT_WELCOME_MSG__"
            }
        }
        self.is_frozen = False
        self.chkpt_dict = {}
        self.save_checkpoint("_internal_start_up")
        self.system_prompt = None

    def save_checkpoint(self, name: str):
        self.chkpt_dict[name] = {
            "conv_id": self.conv_id,
            "parent_item_id": self.conv_dict[self.conv_id]["parent_item_id"],
            "parent_content": self.conv_dict[self.conv_id]["parent_content"],
        }

    def load_checkpoint(self, name: str):
        if name not in self.chkpt_dict:
            raise ValueError(f"Checkpoint {name} not found")
        self.conv_id = self.chkpt_dict[name]["conv_id"]
        self.conv_dict[self.conv_id]["parent_item_id"] = self.chkpt_dict[name]["parent_item_id"]
        self.conv_dict[self.conv_id]["parent_content"] = self.chkpt_dict[name]["parent_content"]
        self.conv_dict[self.conv_id]["pre_generated_reply_id"] = get_msg_id()

    def get_text_item(self, item_type: str, item_id: str, content: str, parent_item_id: Optional[str]) -> Item:
        return Item(
            item_id=item_id,
            conversation_id=self.conv_id,
            item_type=item_type,
            summary=content,
            parent_item_id=parent_item_id,
            data=Data1(
                type="text",
                content=content,
                render_in_streaming=item_type == "question",
                quote_content="",
                chat_model=self.config.chat.chat_model
            )
        )

    def get_base_text_item(self, item_type: str, item_id: str, content: str, parent_item_id: Optional[str]) -> BaseItem:
        return BaseItem(
            item_id=item_id,
            conversation_id=self.conv_id,
            item_type=item_type,
            summary=content,
            parent_item_id=parent_item_id,
            data=BaseData1(
                type="text",
                content=content,
                render_in_streaming=item_type == "question",
                quote_content="",
            )
        )

    def get_conv_id(self) -> str:
        return self.conv_id

    def change_conversion(self, conv_id: str):
        self.conv_id = conv_id

    def freeze_conversion(self) -> str:
        self.is_frozen = True
        return self.conv_id

    def get_advanced_chat_request_body(self, message: str) -> ChatRequestBody:
        items: list[Item] = []
        if self.conv_dict[self.conv_id]["parent_item_id"] is not None:
            items.append(
                self.get_text_item(
                    item_type="reply",
                    item_id=self.conv_dict[self.conv_id]["parent_item_id"],
                    content=self.conv_dict[self.conv_id]["parent_content"],
                    parent_item_id=None
                )
            )
        new_message_id = get_msg_id()
        items.append(
            self.get_text_item(
                item_type="question",
                item_id=new_message_id,
                content=message,
                parent_item_id=self.conv_dict[self.conv_id]["parent_item_id"]
            )
        )

        conv_data = Data(
            conversation_id=self.conv_id,
            items=items,
            pre_generated_reply_id=self.conv_dict[self.conv_id]["pre_generated_reply_id"],
            pre_parent_item_id=new_message_id
        )

        return ChatRequestBody(
            task_uid=get_task_id(),
            data=conv_data
        )

    def get_chat_request_body(self, message: str) -> BaseChatPostBody:
        items: list[BaseItem] = []
        if self.conv_dict[self.conv_id]["parent_item_id"] is not None:
            items.append(
                self.get_base_text_item(
                    item_type="reply",
                    item_id=self.conv_dict[self.conv_id]["parent_item_id"],
                    content=self.conv_dict[self.conv_id]["parent_content"],
                    parent_item_id=None
                )
            )
        new_message_id = get_msg_id()
        items.append(
            self.get_base_text_item(
                item_type="question",
                item_id=new_message_id,
                content=message,
                parent_item_id=self.conv_dict[self.conv_id]["parent_item_id"]
            )
        )

        conv_data = BaseData(
            conversation_id=self.conv_id,
            items=items,
            pre_generated_reply_id=self.conv_dict[self.conv_id]["pre_generated_reply_id"],
            pre_parent_item_id=new_message_id
        )

        return BaseChatPostBody(
            task_uid=get_task_id(),
            data=conv_data
        )

    def chat(self, message: MessageChain, is_advanced: bool = False, is_continue=False, *args, **kwargs) -> AsyncIterator[ModelResponse]:
        assert len(message.messages) == 1
        if is_advanced:
            request_body = self.get_advanced_chat_request_body(message.messages[0].content)
        else:
            request_body = self.get_chat_request_body(message.messages[0].content)
        return self.process_sse(request_body, is_continue)

    def after_reply(self, reply: str, is_continue: bool):
        if self.is_frozen:
            return
        self.conv_dict[self.conv_id]["parent_item_id"] = self.conv_dict[self.conv_id]["pre_generated_reply_id"]
        self.conv_dict[self.conv_id]["parent_content"] = reply
        self.conv_dict[self.conv_id]["pre_generated_reply_id"] = get_msg_id()

        if not is_continue:
            if self.system_prompt is not None:
                self.load_checkpoint(self.system_prompt)
            else:
                self.load_checkpoint("_internal_start_up")

    async def process_sse(self, request_body: ChatRequestBody, is_continue: bool) -> AsyncIterator[ModelResponse]:
        total_reply = ""
        async with self.client.stream('POST', 'https://monica.im/api/custom_bot/chat', content=request_body.model_dump_json()) as response:
            async for line in response.aiter_lines():
                if line.startswith('data:'):
                    event_data = line[5:].strip()
                    data = json.loads(event_data)
                    total_reply += data['text']
                    if data.get('finished', False):
                        self.after_reply(total_reply, is_continue)
                    yield ModelResponse(content=data['text'])

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'cookie': self.config.auth.cookie,
            "origin": "chrome-extension://ofpnmcalabcbjgholdjcjblkibolbppb",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        }

    def get_client(self) -> AsyncClient:
        return AsyncClient(
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
