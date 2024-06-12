from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import time
import requests
import os
import sys
import logging
from langchain_core.messages import HumanMessage, AIMessage

sys.path.append(os.getcwd())
from app.chatbot.chat import Chatbot
from app.common.config import Config
from app.database.schemas import Thread, SubThread, Message
from app.database.thread import ThreadCollection, SubThreadCollection
cfg = Config()


gapo_app = FastAPI()

class GapoMessage(BaseModel):
    id: str
    event: str
    thread_id: int
    from_user_id: int
    to_bot_id: int
    message: dict = None

chatbot = Chatbot()
thread_collection = ThreadCollection()
subthread_collection = SubThreadCollection()

URL = cfg.gapo_api_url
HEADERS = {
    "x-gapo-api-key": os.environ.get("GAPO_API_KEY"),
    "Content-Type": "application/json"
}

def send_message(thread_id: int, bot_id: int, message_id: int, message: str):
    data = {
        "thread_id": thread_id,
        "bot_id": bot_id,
        "message_id": message_id,
        "body":  {
            "type": "text",
            "text": message,
            "is_markdown_text": True
        }
    }
    response = requests.post(URL, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 200:
        logging.debug("Message sent successfully")
    else:
        logging.error(f"Cannot send reply the message to gapo! \
                      Status code {response.status_code}, Response {response.json()}")
    return response.json()['data']

@gapo_app.post("/chatbot247")
async def handle_webhook(event: GapoMessage):
    chat_history = []
    # Check the event type
    if event.event == 'message_created':
        bot_id = str(event.to_bot_id)
        user_id = str(event.from_user_id)
        message_type = event.message.get('thread', {}).get('type')

        if message_type == "group":
            thread_id = str(event.thread_id)
            new_thread = Thread(
                id=str(event.id),
                thread_id=str(event.thread_id),
                from_user_id=str(event.from_user_id),
                to_bot_id=str(event.to_bot_id)
            )
            thread_collection.insert_one(new_thread.model_dump())

            parent_message_id = str(event.message.get('id'))
            new_message = SubThread(
                id=str(event.id),
                event=event.event,
                thread_id=thread_id,
                parent_message_id=str(parent_message_id),
                message_id = str(0),
                from_id=str(event.from_user_id),
                to_id=str(event.to_bot_id),
                message=event.message
            )

        elif message_type == "subthread":
            # get all messages (subthread messsages) in the thread
            parent_message_id = str(event.message.get('thread').get('root_message_id'))
            thread_id = str(event.message.get('thread').get('parent_id'))
            all_subthread_message = subthread_collection.find_by_thread_id(thread_id)
            for subthread in all_subthread_message:
                if subthread.get('from_id') == user_id:
                    chat_history.append(HumanMessage(content=subthread.get('message').get('text')))
                else:
                    chat_history.append(AIMessage(content=subthread.get('message').get('text')))

            # create a new subthread message to insert into the database
            new_message = SubThread(
                id=str(event.id),
                event=event.event,
                thread_id=thread_id,
                parent_message_id=parent_message_id,
                message_id = str(event.message.get('id')),
                from_id=user_id,
                to_id=bot_id,
                message=event.message
            )
            subthread_collection.insert_one(new_message.model_dump())
        
        user_message = str(event.message.get('text'))
        answer = chatbot.chat([], user_message)

        logging.debug(f"Thread ID: {thread_id}, Parent Message ID: {parent_message_id}")

        response_data = send_message(int(thread_id), int(bot_id), int(parent_message_id), answer)

        # Insert the bot reply into the database as a subthread message
        bot_message = Message(id=response_data.get('event_id'), text=answer, metadata=None, type=None, payload=None)
        bot_reply = SubThread(
            id=response_data.get('event_id'),
            event="message_created",
            thread_id=str(response_data.get('thread_id')),
            parent_message_id=parent_message_id,
            message_id=str(response_data.get('message_id')),
            from_id=bot_id,
            to_id=user_id,
            message=bot_message
        )
        subthread_collection.insert_one(bot_reply.model_dump())
    
    else:
        # Unsupported event type
        print(f"Unsupported event type: {event.event}")

    # Return a success response
    return {"status": "ok"}
