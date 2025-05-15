from flask import request, jsonify
from app import db, app
from datetime import datetime, timedelta
import pandas as pd

@app.route('/analyze')
def analyze_data():
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str:
        return jsonify({"error": "No start date provided"}), 400

    try:
        start = datetime.strptime(start_str, '%Y-%m-%d')
        if end_str:
            end = datetime.strptime(end_str, '%Y-%m-%d')
        else:
            end = start + timedelta(days=1)
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    if end <= start:
        return jsonify({"error": "End date must be after start date"}), 400

    query = db.collection('sensors') \
        .where('server_timestamp', '>=', start) \
        .where('server_timestamp', '<', end)

    docs = query.stream()
    data = [doc.to_dict() for doc in docs if 'server_timestamp' in doc.to_dict()]
    if not data:
        return jsonify({"error": "No data for this range"}), 404

    df = pd.DataFrame(data)
    df = df.sort_values(by='server_timestamp')

    temp_threshold = 35
    humidity_threshold = 70
    light_threshold = 800

    temp_exceeds = df[df['temperature'] > temp_threshold]
    humidity_exceeds = df[df['humidity'] > humidity_threshold]
    light_exceeds = df[df['light'] > light_threshold]

    analysis = {
        "range": f"{start_str} to {end.strftime('%Y-%m-%d')}",
        "start": start.isoformat(),
        "end": end.isoformat(),

        "avg_temp": round(float(df['temperature'].mean()), 2),
        "max_temp": round(float(df['temperature'].max()), 2),
        "min_temp": round(float(df['temperature'].min()), 2),
        "median_temp": round(float(df['temperature'].median()), 2),
        "temp_range": round(float(df['temperature'].max() - df['temperature'].min()), 2),
        "temp_exceeds_count": int(len(temp_exceeds)),

        "avg_humidity": round(float(df['humidity'].mean()), 2),
        "max_humidity": round(float(df['humidity'].max()), 2),
        "min_humidity": round(float(df['humidity'].min()), 2),
        "median_humidity": round(float(df['humidity'].median()), 2),
        "humidity_range": round(float(df['humidity'].max() - df['humidity'].min()), 2),
        "humidity_exceeds_count": int(len(humidity_exceeds)),

        "std_light": round(float(df['light'].std()), 2),
        "max_light": round(float(df['light'].max()), 2),
        "min_light": round(float(df['light'].min()), 2),
        "light_range": round(float(df['light'].max() - df['light'].min()), 2),
        "light_exceeds_count": int(len(light_exceeds))
    }

    return jsonify(analysis)
