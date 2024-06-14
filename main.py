from fastapi import FastAPI
from app.gapo.webhook import gapo_app
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

app = FastAPI()

app.mount("/gapo", gapo_app)

# Define the routes
@app.get("/health_check")
def health_check():
    return {"status": "ok"}
