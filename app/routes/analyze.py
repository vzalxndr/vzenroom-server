from flask import request, jsonify
from app import db, app
from datetime import datetime, timedelta
import pandas as pd
import math

def safe_round(value, digits=2):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return round(float(value), digits)

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

        "avg_temp": safe_round(df['temperature'].mean()),
        "max_temp": safe_round(df['temperature'].max()),
        "min_temp": safe_round(df['temperature'].min()),
        "median_temp": safe_round(df['temperature'].median()),
        "temp_range": safe_round(df['temperature'].max() - df['temperature'].min()),
        "temp_exceeds_count": int(len(temp_exceeds)),

        "avg_humidity": safe_round(df['humidity'].mean()),
        "max_humidity": safe_round(df['humidity'].max()),
        "min_humidity": safe_round(df['humidity'].min()),
        "median_humidity": safe_round(df['humidity'].median()),
        "humidity_range": safe_round(df['humidity'].max() - df['humidity'].min()),
        "humidity_exceeds_count": int(len(humidity_exceeds)),

        "avg_light": safe_round(df['humidity'].mean()),
        "std_light": safe_round(df['light'].std()),
        "max_light": safe_round(df['light'].max()),
        "min_light": safe_round(df['light'].min()),
        "light_range": safe_round(df['light'].max() - df['light'].min()),
        "light_exceeds_count": int(len(light_exceeds))
    }

    return jsonify(analysis)
