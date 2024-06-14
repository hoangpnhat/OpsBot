import os
import sys
from typing import TypeVar, List
from app.common.config import logger
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.chatbot.chat import Chatbot
from app.gapo.messages.base import BaseMessage

GapoMessage = TypeVar('GapoMessage')

class DirectMessage(BaseMessage):
    def __init__(self, 
                 event: GapoMessage, 
                 msg_sender: MessageSender, 
                 msg_getter: MessageGetter,
                 chatbot: Chatbot,
                 n_messages: int = 6) -> None:
        super().__init__(event, msg_sender, msg_getter, chatbot, n_messages)

        self.parent_message_id = event.message.get('id')
        # for direct message, the thread_id is the same as the parent_thread_id
        self.thread_id = event.thread_id
        self.parent_thread_id = self.thread_id

        logger.debug("=" * 10 + f"Direct message with user: {self.user_id}, thread_id: {self.thread_id}, message_id: {self.parent_message_id}" + "=" * 10)

