import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from flask import request, jsonify, send_file
from app import db, app
from datetime import datetime, timedelta
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import numpy as np

@app.route('/plot')
def plot_data():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    plot_type = request.args.get('type', 'all')
    color = request.args.get('color', None)

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
            .where('server_timestamp', '<', end)

        docs = query.stream()
        data = [doc.to_dict() for doc in docs if 'server_timestamp' in doc.to_dict()]
        if not data:
            return jsonify({"error": "No data available for the specified range"}), 404

        df = pd.DataFrame(data)
        df = df.sort_values(by='server_timestamp')

        buf = io.BytesIO()
        plt.figure(figsize=(10, 5))

        title_range = f"{start_str} to {end.strftime('%Y-%m-%d')}"

        if plot_type == 'temperature':
            x = df['server_timestamp'].map(mdates.date2num)
            y = df['temperature']
            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            norm = Normalize(vmin=y.min(), vmax=y.max())
            lc = LineCollection(segments, cmap='coolwarm', norm=norm)
            lc.set_array(y)
            lc.set_linewidth(2)
            plt.title(f"Temperature from {title_range}")
            plt.gca().add_collection(lc)
            plt.colorbar(lc, label='Temperature (°C)')
            plt.xlim(x.min(), x.max())
            plt.ylim(y.min() - 1, y.max() + 1)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)

        elif plot_type == 'humidity':
            plt.plot(df['server_timestamp'], df['humidity'], marker='o', color=color or 'green')
            plt.title(f"Humidity from {title_range}")
            plt.ylabel("Humidity (%)")
            plt.xlabel("Time")
            plt.grid(True)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)

        elif plot_type == 'light':
            plt.plot(df['server_timestamp'], df['light'], marker='o', color=color or 'orange')
            plt.title(f"Light level from {title_range}")
            plt.ylabel("Light")
            plt.xlabel("Time")
            plt.grid(True)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)

        elif plot_type == 'th_correlation':
            plt.scatter(df['temperature'], df['humidity'], color=color or 'purple')
            plt.title(f"Humidity vs Temperature ({title_range})")
            plt.xlabel("Temperature (°C)")
            plt.ylabel("Humidity (%)")
            plt.grid(True)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)

        elif plot_type == 'all':
            fig, axs = plt.subplots(4, 1, figsize=(10, 16))

            axs[0].plot(df['server_timestamp'], df['temperature'], marker='o', color=color or 'blue')
            axs[0].set_title("Temperature")
            axs[0].set_ylabel("°C")
            axs[0].grid(True)
            axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[0].get_xticklabels():
                label.set_rotation(45)

            axs[1].plot(df['server_timestamp'], df['humidity'], marker='o', color=color or 'green')
            axs[1].set_title("Humidity")
            axs[1].set_ylabel("%")
            axs[1].grid(True)
            axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[1].get_xticklabels():
                label.set_rotation(45)

            axs[2].plot(df['server_timestamp'], df['light'], marker='o', color=color or 'orange')
            axs[2].set_title("Light Level")
            axs[2].set_ylabel("Lux")
            axs[2].grid(True)
            axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[2].get_xticklabels():
                label.set_rotation(45)

            axs[3].scatter(df['temperature'], df['humidity'], c=color or 'purple')
            axs[3].set_title("Humidity vs Temperature")
            axs[3].set_xlabel("Temp (°C)")
            axs[3].set_ylabel("Humidity (%)")
            axs[3].grid(True)
            for label in axs[3].get_xticklabels():
                label.set_rotation(45)

            fig.suptitle(f"Sensor Data: {title_range}", fontsize=16)
            plt.tight_layout(rect=[0, 0.03, 1, 0.97])

        else:
            return jsonify(
                {"error": "Invalid plot type. Use temperature, humidity, light, th_correlation, or all."}), 400

        plt.tight_layout()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return send_file(buf, mimetype='image/png')

    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
