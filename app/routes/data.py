from flask import request, jsonify
from app import db, app
from firebase_admin import firestore
from app.services.telegram import send_telegram_alert

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    required_keys = ['temperature', 'humidity', 'light']
    temperature_threshold = 30

    if not data:
        return jsonify({"error": "No JSON received"}), 400
    if not all(k in data for k in required_keys):
        return jsonify({"error": "Missing sensor fields"}), 400

    data["server_timestamp"] = firestore.SERVER_TIMESTAMP
    db.collection('sensors').add(data)

    if "temperature" in data and data["temperature"] > temperature_threshold:
        send_telegram_alert(data)

    print("Received and stored data")
    return jsonify({"status": "success"}), 200
