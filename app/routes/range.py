from flask import request, jsonify
from app import db, app
from datetime import datetime, timedelta

@app.route('/range')
def get_data_range():
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

        if end <= start:
            return jsonify({"error": "End date must be after start date"}), 400

        query = db.collection('sensors') \
            .where('server_timestamp', '>=', start) \
            .where('server_timestamp', '<', end) \
            .order_by('server_timestamp')

        docs = query.stream()
        data = [doc.to_dict() for doc in docs]

        for entry in data:
            if 'server_timestamp' in entry and entry['server_timestamp']:
                entry['server_timestamp'] = entry['server_timestamp'].isoformat()

        return jsonify(data)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
