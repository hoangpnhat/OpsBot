from fastapi import FastAPI, Response
from pydantic import BaseModel
import os
import sys
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.chatbot.chat import Chatbot
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.gapo.messages.direct_message import DirectMessage
from app.gapo.messages.subthread import SubThread
from app.common.config import cfg, logger

gapo_app = FastAPI()
class GapoMessage(BaseModel):
    id: str
    event: str
    thread_id: int
    from_user_id: int
    to_bot_id: int
    message: dict = None

chatbot = Chatbot()
message_sender = MessageSender()
message_getter = MessageGetter()

@gapo_app.post("/chatbot247")
async def handle_webhook(event: GapoMessage):
    """
    Webhook to handle messages from Gapo and send responses back once the user sends a message to the bot

    Args:
        event (GapoMessage): The event from Gapo
    
    Returns:
        Response: A response object
    """
    # Check the event type
    if event.event == 'message_created':
        message_type = event.message.get('thread', {}).get('type')
        handler = None
        if message_type in ("group", "subthread"):
            handler = SubThread(event, message_sender, message_getter, chatbot)
        elif message_type == "direct":
            handler = DirectMessage(event, message_sender, message_getter, chatbot)
        
        if handler is not None:
            answer = "Bạn đã hết tiền, tôi không thể trả lời cho bạn. Vui lòng nạp card! PAY TO WIN" 
            logger.debug(f"Chat history: {handler.get_chat_history()}")
            handler.send_answer(answer)
    
    else:
        # Unsupported event type
        logger.critical(f"Unsupported event type: {event.event}. The body is {event}")

    # Return a success response
    return Response(status_code=200)