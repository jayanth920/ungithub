from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

@app.get("/ping")
def ping():
    return {"message": "pong"}
