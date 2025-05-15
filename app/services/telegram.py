import requests
from datetime import datetime
from app import app
from io import BytesIO

def send_telegram_alert(data):
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bot_token = app.config['TELEGRAM_BOT_TOKEN']
    chat_id = app.config['TELEGRAM_CHAT_ID']

    message = (f"⚠️ ALERT! High Temperature Detected! 🔥\n\n"
               f"🌡️ Temperature: {data['temperature']}°C\n"
               f"🕒 Timestamp: {current_timestamp}")

    send_msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    msg_params = {'chat_id': chat_id, 'text': message}
    requests.get(send_msg_url, params=msg_params)
