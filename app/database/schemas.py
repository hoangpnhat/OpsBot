from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List

class Thread(BaseModel):
    id: str
    thread_id: str
    from_user_id: str
    to_bot_id: str


class UserSchema(BaseModel):
    name: str
    id: str
    avatar: HttpUrl | str
    status_verify: int
    type: str


class Mention(BaseModel):
    target: str
    length: int
    offset: int

class MessageMetadata(BaseModel):
    preview_link: Optional[HttpUrl] = None
    mentions: List[Mention]
    payload: str
    is_markdown_text: bool
    reply_to_message: Dict[str, Any]

class Message(BaseModel):
    id: str
    text: str
    type: str | None
    metadata: MessageMetadata | None
    payload: str | None

class SubThread(BaseModel):
    id: str
    event: str
    thread_id: str
    parent_message_id: str
    message_id: str
    from_id: str
    to_id: str
    message: Message