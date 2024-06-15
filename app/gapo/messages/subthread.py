import os
import sys
from typing import TypeVar, List
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.common.config import logger
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.chatbot.chat import Chatbot
from app.gapo.messages.base import BaseMessage

GapoMessage = TypeVar('GapoMessage')

class SubThread(BaseMessage):
    def __init__(self, 
                 event: GapoMessage, 
                 msg_sender: MessageSender, 
                 msg_getter: MessageGetter,
                 chatbot: Chatbot,
                 n_messages: int = 6) -> None:
        super().__init__(event, msg_sender, msg_getter, chatbot, n_messages)
        # This is the start of a subthread
        if self.message_type == "group":
            self.thread_id = event.thread_id
            self.parent_thread_id = self.thread_id
            self.parent_message_id = event.message.get('id')
        # This is a reply to a message in a subthread
        elif self.message_type == "subthread":
            self.parent_thread_id = event.message.get('thread').get('parent_id')
            self.thread_id = event.thread_id
            self.parent_message_id = event.message.get('thread').get('root_message_id')

        logger.debug("=" * 10 + f"Chat group - thread_id: {self.thread_id}, parent_thread_id: {self.parent_thread_id} parent_message_id: {self.parent_message_id}" + "=" * 10)
    

