import os
import sys
from typing import TypeVar, List
from langchain_core.messages import HumanMessage, AIMessage
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.common.config import logger
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.chatbot.chat import Chatbot
from app.utils.str import extract_dict_from_string
GapoMessage = TypeVar('GapoMessage')


class BaseMessage:
    def __init__(self, 
                 event: GapoMessage,
                 msg_sender: MessageSender, 
                 msg_getter: MessageGetter,
                 chatbot: Chatbot,
                 n_messages: int = 6) -> None:
        
        self.msg_sender = msg_sender
        self.msg_getter = msg_getter
        self.chatbot = chatbot
        self.event = event
        self.bot_id = event.to_bot_id
        self.user_id = event.from_user_id
        self.thread_id = None
        self.parent_thread_id = None
        self.parent_message_id = None
        self.message_type = event.message.get('thread', {}).get('type')
        self.user_message = event.message.get('text')
        self.page_size = n_messages
        
    def get_chat_history(self) -> List[HumanMessage | AIMessage]:
        """
        This function retrieves the chat history from the subthread or direct message by thread_id

        Returns:
            List[HumanMessage | AIMessage]: Chat history, it is a list of messages to feed to the chatbot

        """
        chat_history = []
        messages = self.msg_getter.get_messages(self.thread_id, self.page_size)
        for i, msg in enumerate(messages):
            # Skip the first message, because it is user query
            if i == 0:
                continue
            msg_text = msg.get('body').get('text')
            if msg.get('sender_id') == self.bot_id:
                chat_history.insert(0, AIMessage(msg_text))
            else:
                chat_history.insert(0, HumanMessage(msg_text))

        return chat_history
    
    def get_anwser_from_bot(self, 
                            user_message: str = None, 
                            chat_history: List[HumanMessage | AIMessage] = None
                            ) -> str:
        """
        This function gets the answer from the chatbot

        Args:
            user_message (str): The message from the user. If None, it will use the user_message from the event webhook
            chat_history (List[HumanMessage | AIMessage]): The chat history, if you want to use a customs chat history. 
                                            If None, it will use the chat history from the subthread or direct message

        Returns:
            str: The answer from the chatbot
        """

        chat_history = chat_history or self.get_chat_history()
        logger.debug(f"Chat history: {chat_history}")
        user_message = user_message or self.user_message
        return self.chatbot.chat(chat_history, user_message)

    def send_answer(self, answer: str = None) -> bool:
        """
        This function sends the answer to the user.

        Args:
            answer (str): The answer to send, use it if you want to send a customs answer, dont get answer from chatbot. 
                            If None, it will get the answer from the chatbot

        """
        answer = answer or self.get_anwser_from_bot()

        json_output= extract_dict_from_string(answer)
        if json_output['status'] =="clarified":
            mention = {
                                "pic_gapo_name": json_output['pic_gapo_name'],
                                "pic_gapo_id": json_output['pic_gapo_id']
                    }
            logger.debug(f"mention: {mention}")
            
        logger.debug(f"Answer: {answer}")
        if self.message_type in ("group", "subthread"):
            if self.thread_id is None or self.parent_message_id is None or self.bot_id is None:
                logger.error(f"Cannot send message to subthread. \
                                Missing value(s) thread_id: {self.thread_id}, \
                                parent_message_id: {self.parent_message_id} or bot_id: {self.bot_id}"
                            )
                return False
            self.msg_sender.send_text_message_to_subthread(self.thread_id, self.bot_id, self.parent_message_id, answer, mention)
        elif self.message_type == "direct":
            if self.user_id is None or self.bot_id is None:
                logger.error(f"Cannot send message to the User. \
                                Missing user_id: {self.user_id} or bot_id: {self.bot_id}"
                            )
                return False
            self.msg_sender.send_text_message_to_user(self.user_id, self.bot_id, answer)
        else:
            logger.error(f"Message type {self.message_type} not supported")
            return False
        return True