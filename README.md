This is the Python backend for the Monitoring System. It receives data from an ESP32 device, stores it in Firebase, and provides an API for data analysis and visualization.

The corresponding frontend can be found here: [https://github.com/vzalxndr/vzenroom-beta](https://github.com/vzalxndr/vzalxndr.github.io)

---

## Quick Setup

To run this project locally, you need to configure two things:

#### 1. Firebase Credentials

-   Place your Google Firebase service account key in a file named `firebase-credentials.json` in the root directory of the project.

#### 2. Environment Variables

-   Create a `.env` file in the root directory and add your Telegram bot credentials:

```env
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID="YOUR_TARGET_CHAT_ID_HERE"



After configuring the credentials, install the dependencies and run the server:
pip install -r requirements.txt
