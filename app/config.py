import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    FIREBASE_CRED_PATH = os.getenv("FIREBASE_CRED_PATH")

    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_RUN_PORT", 5000))


