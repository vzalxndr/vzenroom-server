import requests
from datetime import datetime
from app import app

def send_telegram_alert(data):
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    bot_token = app.config['TELEGRAM_BOT_TOKEN']
    chat_id = app.config['TELEGRAM_CHAT_ID']

    message = (f"⚠️ ALERT! High Temperature Detected! 🔥\n\n"
               f"🌡️ Temperature: {data['temperature']}°C\n"
               f"🕒 Timestamp: {current_timestamp}\n"
               "Please check the system! ⚠️")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    params = {
        'chat_id': chat_id,
        'text': message
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("Telegram alert sent successfully!")
        else:
            print(f"Failed to send Telegram alert. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
