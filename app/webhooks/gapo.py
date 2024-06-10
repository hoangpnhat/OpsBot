from fastapi import FastAPI, Request
from pydantic import BaseModel
import json

gapo_app = FastAPI()

class GapoMessage(BaseModel):
    id: str
    event: str
    thread_id: int
    from_user_id: int
    to_bot_id: int
    message: dict = None

@gapo_app.post("/chatbot247")
async def handle_webhook(event: GapoMessage):
    # Check the event type
    if event.event == 'thread_created':
        # Save the thread to the database
        # Create new conversation
        # Call LLM to generate a response
        print(f"New thread created: {event.thread_id}, from user: {event.from_user_id}, to bot: {event.to_bot_id}")
    elif event.event == 'message_created':
        # Save the message to the database
        # Load conversation history
        # Call LLM to generate a response
        pass
    
    else:
        # Unsupported event type
        print(f"Unsupported event type: {event.event}")
        # Create a response
    
    # Call API to create message

    # Return a success response
    return {"status": "ok"}
