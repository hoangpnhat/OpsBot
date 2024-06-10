from fastapi import FastAPI
from app.webhooks.gapo import gapo_app

app = FastAPI()

app.mount("/gapo", gapo_app)

# Define the routes
@app.get("/health_check")
def health_check():
    return {"status": "ok"}
