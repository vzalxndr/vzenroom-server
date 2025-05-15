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
               f"🕒 Timestamp: {current_timestamp}\n"
               "📈 Sending temperature graph...")

    send_msg_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    msg_params = {'chat_id': chat_id, 'text': message}
    requests.get(send_msg_url, params=msg_params)

    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        plot_url = f"https://vzenroom-server.fly.dev/plot?start={start_date}&type=temperature"

        plot_response = requests.get(plot_url)
        if plot_response.status_code == 200:
            send_photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
            files = {'photo': ('graph.png', BytesIO(plot_response.content))}
            photo_params = {'chat_id': chat_id}
            photo_resp = requests.post(send_photo_url, params=photo_params, files=files)

            if photo_resp.status_code != 200:
                print(f"Failed to send photo: {photo_resp.status_code}")
                print(photo_resp.text)

    except Exception as e:
        print(f"Error sending Telegram photo: {e}")
