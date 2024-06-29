import os
import sys
from typing import TypeVar, List, Dict
from langchain_core.messages import HumanMessage, AIMessage
from app.common.config import logger, cfg
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.chatbot.chat import Chatbot
from app.utils.str import extract_and_remove_dict_from_string
from app.utils.image import convert_image_to_base64, download_image

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

    
    def convert_image_message(self, message: Dict) -> HumanMessage:
        msg_type = message.get('body', {}).get('type')
        if msg_type in ["file", "image", "multi_image"]:
            image_urls = message.get('body', {}).get('media', [])
            # get the text in message
            content = [{"type": "text", "text": message.get('body', {}).get('text')}]

            # get the image in message
            for image_url in image_urls:
                image, image_path = download_image(image_url)
                img_base64 = convert_image_to_base64(image, 
                                                     quality=cfg.image_quality,
                                                     max_size=(cfg.image_with, cfg.image_height))
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                })
            return HumanMessage(content=content)
        return None
        
    def get_chat_history(self) -> List[HumanMessage | AIMessage]:
        """
        This function retrieves the chat history from the subthread or direct message by thread_id

        Returns:
            List[HumanMessage | AIMessage]: Chat history, it is a list of messages to feed to the chatbot

        """
        chat_history = []
        if self.message_type == "group":
            return chat_history
        messages = self.msg_getter.get_messages(self.thread_id, self.page_size)
        for i, msg in enumerate(messages):
            # Skip the first message, because it is user query
            msg_type = msg.get('body', {}).get('type')
            human_msg = None
            if i == 0 or msg.get("deleted", False):
                human_msg = self.convert_image_message(msg)
                if human_msg:
                    chat_history.insert(0, human_msg)
                continue

            # Verify message type
            if msg_type == "carousel":
                msg_text = msg.get('body').get('metadata').get('carousel_cards', [])[0].get('title')
            else:
                msg_text = msg.get('body', {}).get('text')

            if str(msg.get('sender', {}).get("id")) == str(self.bot_id):
                chat_history.insert(0, AIMessage(msg_text))
            else:
                # Create a human message with image if there is an image in the message
                human_msg = self.convert_image_message(msg)
                # Otherwise, create a human message with text
                human_msg = human_msg or HumanMessage(msg_text)
                chat_history.insert(0, human_msg)
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
        user_message = user_message or self.user_message
        return self.chatbot.chat(chat_history, 
                                 user_message, 
                                 self.user_id)

    def send_answer(self, answer: str = None) -> Dict | None:
        """
        This function sends the answer to the user.

        Args:
            answer (str): The answer to send, use it if you want to send a customs answer, dont get answer from chatbot. 
                            If None, it will get the answer from the chatbot

        """
        answer = answer or self.get_anwser_from_bot()
        answer, json_output= extract_and_remove_dict_from_string(answer)
        mention = None
        try:
            if json_output.get('status') != "clarifying":
                mention = [
                                {
                                    "pic_gapo_name": user['pic_gapo_name'],
                                    "pic_gapo_id": user['pic_gapo_id']
                                } 
                        for user in json_output['mention']
                        ]
        except:
            pass
        logger.debug(f"Answer: {answer}")
        logger.debug(f"mention: {mention}")

        if self.message_type in ("group", "subthread"):
            if self.parent_thread_id is None or self.parent_message_id is None or self.bot_id is None:
                logger.error(f"Cannot send message to subthread. \
                                Missing value(s) parent_thread_id: {self.parent_thread_id}, \
                                parent_message_id: {self.parent_message_id} or bot_id: {self.bot_id}"
                            )
                return None
            return self.msg_sender.send_text_message_to_subthread(self.parent_thread_id, self.bot_id, self.parent_message_id, answer, mention)
        elif self.message_type == "direct":
            if self.user_id is None or self.bot_id is None:
                logger.error(f"Cannot send message to the User. \
                                Missing user_id: {self.user_id} or bot_id: {self.bot_id}"
                            )
                return None
            return self.msg_sender.send_text_message_to_user(self.user_id, self.bot_id, answer)
        else:
            logger.error(f"Message type {self.message_type} not supported")
            return None