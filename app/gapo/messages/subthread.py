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
            self.thread_id = self.parent_thread_id
            self.parent_message_id = event.message.get('thread').get('root_message_id')

        logger.debug("=" * 10 + f"Chat group - thread_id: {self.thread_id}, parent_thread_id: {self.parent_thread_id} parent_message_id: {self.parent_message_id}" + "=" * 10)
    
    def send_answer(self, answer: str = None) -> bool:
        """
        This function sends the answer to the user.

        Args:
            answer (str): The answer to send, use it if you want to send a customs answer, dont get answer from chatbot. 
                            If None, it will get the answer from the chatbot

        """
        if self.thread_id is None or self.parent_message_id is None or self.bot_id is None:
            logger.error(f"Cannot send message to subthread. \
                                Missing value(s) thread_id: {self.thread_id}, \
                                parent_message_id: {self.parent_message_id} or bot_id: {self.bot_id}"
                            )
            return False

        mention = {
                            "description": "Find the sum of all the multiples of 3 or 5 below 1000.",
                            "pic_gapo_name": "@VDM.AI.Phạm Nhật Hoàng",
                            "pic_gapo_id": 1359166530
                        }
        self.msg_sender.send_text_with_mention_to_subthread(self.thread_id, 
                                                            self.bot_id, 
                                                            self.parent_message_id, 
                                                            answer, 
                                                            mention)
