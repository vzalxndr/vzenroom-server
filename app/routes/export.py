import io
import pandas as pd
from flask import request, jsonify, send_file
from app import db, app
from datetime import datetime, timedelta

@app.route('/export')
def export_data():
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
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    filename = f"data_{start.strftime('%Y-%m-%d')}_to_{end.strftime('%Y-%m-%d')}.csv"
    return send_file(buf, mimetype='text/csv', as_attachment=True, download_name=filename)
