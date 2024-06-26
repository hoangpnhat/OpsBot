from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime

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

class LastMessage(BaseModel):
    thread_id: str
    message_id: str
    sender_id: str
    bot_id: str
    message_sent_at: datetime
    survey_sent: bool
    message_type: str
    survey_sent_at: datetime | None
    survey_id: str | None
    reminder_sent: bool | None
    reminder_sent_at: datetime | None

class SurveySchema(BaseModel):
    thread_id: str
    message_id: str
    send_at: datetime | None
    is_completed: bool | None
    completed_at: datetime | None
    question: str
    feedback: str | None
    feedback_id: str | None