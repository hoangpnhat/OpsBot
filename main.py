from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv(), override=True)

from app.gapo.webhook import gapo_app

app = FastAPI()

app.mount("/gapo", gapo_app)

# Define the routes
@app.get("/")
def health_check():
    return JSONResponse(content={"status": "ok"})

@app.get("/logs")
def get_logs(n_lines: int = -1):
    try:
        if os.environ.get("ENV") == "dev":
            log_file_path = os.environ.get("DEV_LOG_FILE_PATH", "./logs/dev_data.log")
        else:
            log_file_path = os.environ.get("PRD_LOG_FILE_PATH", "./logs/data.log")
        with open(log_file_path, "r", encoding='utf-8') as f:
            logs = f.readlines()
            # logs = logs.split("\u001b[0m\n\u001b")
            if n_lines > 0:
                logs = logs[-n_lines:]
        # return logs
        return JSONResponse(content={"log_file": log_file_path,"logs": logs})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})