from typing import List, Optional, Union

from pydantic import BaseModel


class BaseData1(BaseModel):
    type: str
    content: str
    render_in_streaming: Optional[bool] = None
    quote_content: Optional[str] = None


class BaseItem(BaseModel):
    item_id: str
    conversation_id: str
    item_type: str
    summary: str
    data: BaseData1
    parent_item_id: Optional[str] = None


class BaseData(BaseModel):
    conversation_id: str
    items: List[BaseItem]
    pre_generated_reply_id: str
    pre_parent_item_id: str
    origin: str = 'chrome-extension://ofpnmcalabcbjgholdjcjblkibolbppb/chatTab.html?tab=chat&botName=Monica&botUid=monica'
    origin_page_title: str = "聊天 - Monica"
    trigger_by: str = 'auto'


class SysSkillListItem(BaseModel):
    allow_user_modify: Optional[bool] = None
    enable: bool
    force_enable: Optional[bool] = None
    uid: str


class SysSkillWebAccess(BaseModel):
    uid: str = 'web_access'
    force_enable: bool = False
    enable: bool = True
    allow_user_modify: bool = False


class SysSkillArtifacts(BaseModel):
    uid: str = 'artifacts'
    enable: bool = False


class ToolData(BaseModel):
    sys_skill_list: List[Union[SysSkillWebAccess, SysSkillArtifacts]] = [SysSkillWebAccess(), SysSkillArtifacts()]


class BaseChatPostBody(BaseModel):
    task_uid: str
    bot_uid: str = 'monica'
    data: BaseData
    language: str = 'auto'
    locale: str = 'zh_CN'
    task_type: str = "chat_with_custom_bot"
    tool_data: ToolData = ToolData()
    ai_resp_language: str = 'Chinese (Simplified)'