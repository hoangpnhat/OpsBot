from fastapi import FastAPI, Response
from pydantic import BaseModel
import os
import sys
from langfuse.decorators import observe, langfuse_context
from langfuse.callback import CallbackHandler
import time
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from functools import partial
if os.getcwd() not in sys.path: sys.path.append(os.getcwd())
from app.chatbot.chat import Chatbot
from app.gapo.create_message import MessageSender
from app.gapo.get_message import MessageGetter
from app.gapo.messages.direct_message import DirectMessage
from app.gapo.messages.subthread import SubThread
from app.common.config import cfg, logger
from app.gapo.survey import SurveyThread
from app.common.timing import timing

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
survey = SurveyThread()


def survey_scheduler():
    """
    This function sends the survey to the available threads
    """
    try:
        survey.send_reminder()
        survey.send_survey()
        return Response(status_code=200, content="Survey sent successfully")
    except Exception as e:
        exc_type, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        msg = f"Error while sending survey: {e}. Error type: {exc_type}, file name {fname}, line no {exc_tb.tb_lineno}"
        logger.error(msg)
        return Response(status_code=500, content=msg)


# Create a subprocess to call function send_survey every 3 minutes
SCHERDULED_INTERVAL = os.environ.get("SCHEDULER_INTERVAL_MINS", 5)
# Set up the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(survey_scheduler, 'interval', seconds=int(SCHERDULED_INTERVAL)*60)
scheduler.start()

def scheduler_shutdown():
    scheduler.shutdown()
gapo_app.add_event_handler("shutdown", scheduler_shutdown)


@gapo_app.post("/chatbot247")
@timing
@observe()
async def handle_webhook(event: GapoMessage):
    """
    Webhook to handle messages from Gapo and send responses back once the user sends a message to the bot

    Args:
        event (GapoMessage): The event from Gapo
    
    Returns:
        Response: A response object
    """
    logger.debug(f"Received event: {event}")
    # check if this is the feedback message from user
    msg_type = event.message.get('type')

    loop = asyncio.get_event_loop()
    if msg_type == "quick_reply":
        feedback_id = str(event.message.get('payload'))
        thread_id = str(event.thread_id)
        feedback = event.message.get('text')
        loop.run_in_executor(None, survey.update_feedback, thread_id, feedback, feedback_id)
        return Response(status_code=200)

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
            response = await asyncio.get_event_loop().run_in_executor(None, handler.send_answer) 
            session_id = "NOT_FOUND_SESSION_ID"
            if response:
                logger.debug(f"Sent message: {response}")
                # use sub_thread_id to keep the session for langfuse tracing
                if message_type in ("group", "subthread"):
                    session_id = str(response.get('sub_thread_id'))
                elif message_type == "direct":
                    session_id = str(response.get('thread_id'))
                
                # save the last message to send survey
                loop.run_in_executor(None,
                                     partial(survey.save_last_message,
                                             thread_id=str(session_id),
                                             message_id=str(response.get('message_id')),
                                             sender_id=str(handler.bot_id),
                                             bot_id=str(handler.bot_id),
                                             message_type="reply"
                                             )
                                    )

        loop.run_in_executor(None,
                             partial(langfuse_context.update_current_trace,
                                     name="Gapo-Chatbot247",
                                     user_id=event.from_user_id,
                                     session_id=session_id,
                                     metadata={
                                         "message_type": message_type,
                                         "sub_thread_id": session_id,
                                     }
                                     )
                             )

    
    else:
        # Unsupported event type
        logger.critical(f"Unsupported event type: {event.event}. The body is {event}")
        return Response(status_code=400, content=f"Unsupported event type {event.event}")
    loop.run_in_executor(None, langfuse_handler.flush)
    # Return a success response
    return Response(status_code=200)


@gapo_app.get("/send_survey")
def send_survey():
    survey_scheduler()
    return Response(content="Triggered survey successfully", status_code=200)

