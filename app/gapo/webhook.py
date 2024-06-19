from fastapi import FastAPI, Response
from pydantic import BaseModel
import os
import sys
from langfuse.decorators import observe, langfuse_context
from langfuse.callback import CallbackHandler
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.chatbot.chat import Chatbot
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.gapo.messages.direct_message import DirectMessage
from app.gapo.messages.subthread import SubThread
from app.common.config import cfg, logger

gapo_app = FastAPI()
langfuse_handler = CallbackHandler()
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
@observe()
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
            answer = "Xin lỗi hiện tại tôi không thể hỗ trợ bạn, vui lòng liên hệ với bộ phận Value Delivery Management để được hỗ trợ" 
            logger.debug(f"Chat history: {handler.get_chat_history()}")
            response = handler.send_answer()
            session_id = "NOT_FOUND_SESSION_ID"
            if response:
                logger.debug(f"Sent message: {response}")
                # use sub_thread_id to keep the session for langfuse tracing
                if message_type in ("group", "subthread"):
                    session_id = str(response.get('sub_thread_id'))
                elif message_type == "direct":
                    session_id = str(response.get('thread_id'))

        langfuse_context.update_current_trace(
            name="Gapo-Chatbot247",
            user_id=event.from_user_id, 
            session_id=session_id, 
            metadata={
                "message_type": message_type,
                "sub_thread_id": session_id, 
                }
        )

    
    else:
        # Unsupported event type
        logger.critical(f"Unsupported event type: {event.event}. The body is {event}")
        return Response(status_code=400, content=f"Unsupported event type {event.event}")
    langfuse_handler.flush()
    # Return a success response
    return Response(status_code=200)