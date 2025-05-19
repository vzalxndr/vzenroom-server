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
from scipy.interpolate import UnivariateSpline

primary_color = '#4d6894'
secondary_color = '#f0c851'
accent_color = '#f0c851'
warning_color = '#f0c851'
grid_color = '#e0e0e0'
shadow_color_1 = '#4d6894'
shadow_color_2 = '#f0c851'
shadow_alpha = 0.15

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['grid.color'] = grid_color
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def apply_smoothing(x, y, k):
    try:
        if len(x) > k:
            spline = UnivariateSpline(x, y, k=k)
            return spline(x)
    except Exception:
        pass
    return y

@app.route('/plot')
def plot_data():
    start_str = request.args.get('start')
    end_str = request.args.get('end')
    plot_type = request.args.get('type', 'all')
    color = request.args.get('color', None)

    smooth_k_raw = request.args.get('smooth', None)
    smooth_k = None
    if smooth_k_raw is not None:
        try:
            smooth_k = int(smooth_k_raw)
            if smooth_k < 1 or smooth_k > 5:
                smooth_k = None
        except ValueError:
            pass

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
            if smooth_k:
                y = apply_smoothing(x, y, smooth_k)

            points = np.array([x, y]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            norm = Normalize(vmin=y.min(), vmax=y.max())
            lc = LineCollection(segments, cmap='coolwarm', norm=norm, linewidth=1.5)
            lc.set_array(y)
            plt.title(f"Temperature from {title_range}")
            plt.subplots_adjust(top=0.85)
            plt.gca().add_collection(lc)
            plt.colorbar(lc, label='Temperature (°C)')
            plt.xlim(x.min(), x.max())
            plt.grid(True)
            plt.ylim(y.min() - 1, y.max() + 1)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)

        elif plot_type == 'humidity':
            x = df['server_timestamp'].map(mdates.date2num)
            y = df['humidity']
            if smooth_k:
                y = apply_smoothing(x, y, smooth_k)
            plt.plot(x, y, color=color or primary_color, linewidth=1.5)
            plt.title(f"Humidity from {title_range}")
            plt.ylabel("Humidity (%)")
            plt.xlabel("Time")
            plt.grid(True)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)
            plt.fill_between(x, y, y.min() - 1, color=color or shadow_color_1, alpha=shadow_alpha)

        elif plot_type == 'light':
            x = df['server_timestamp'].map(mdates.date2num)
            y = df['light']
            if smooth_k:
                y = apply_smoothing(x, y, smooth_k)
            plt.plot(x, y, color=color or primary_color, linewidth=1.5)
            plt.title(f"Light level from {title_range}")
            plt.ylabel("Light")
            plt.xlabel("Time")
            plt.grid(True)
            plt.gca().xaxis_date()
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            plt.xticks(rotation=45)
            plt.fill_between(x, y, y.min() - 1, color=color or shadow_color_1, alpha=shadow_alpha)

        elif plot_type == 'th_correlation':
            plt.scatter(df['temperature'], df['humidity'], color=color or primary_color, s=20)
            plt.title(f"Humidity vs Temperature ({title_range})")
            plt.xlabel("Temperature (°C)")
            plt.ylabel("Humidity (%)")
            plt.grid(True)

        elif plot_type == 'all':
            fig, axs = plt.subplots(4, 1, figsize=(10, 16))
            plt.subplots_adjust(top=0.95)

            x_temp = df['server_timestamp'].map(mdates.date2num)
            y_temp = df['temperature']
            if smooth_k:
                y_temp = apply_smoothing(x_temp, y_temp, smooth_k)
            axs[0].plot(x_temp, y_temp, color=color or secondary_color, linewidth=1.5)
            axs[0].set_title("Temperature")
            axs[0].set_ylabel("°C")
            axs[0].grid(True)
            axs[0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[0].get_xticklabels():
                label.set_rotation(45)
            axs[0].fill_between(x_temp, y_temp, y_temp.min() - 1, color=color or shadow_color_2, alpha=shadow_alpha)

            x_hum = df['server_timestamp'].map(mdates.date2num)
            y_hum = df['humidity']
            if smooth_k:
                y_hum = apply_smoothing(x_hum, y_hum, smooth_k)
            axs[1].plot(x_hum, y_hum, color=color or primary_color, linewidth=1.5)
            axs[1].set_title("Humidity")
            axs[1].set_ylabel("%")
            axs[1].grid(True)
            axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[1].get_xticklabels():
                label.set_rotation(45)
            axs[1].fill_between(x_hum, y_hum, y_hum.min() - 1, color=color or shadow_color_1, alpha=shadow_alpha)

            x_light = df['server_timestamp'].map(mdates.date2num)
            y_light = df['light']
            if smooth_k:
                y_light = apply_smoothing(x_light, y_light, smooth_k)
            axs[2].plot(x_light, y_light, color=color or secondary_color, linewidth=1.5)
            axs[2].set_title("Light Level")
            axs[2].set_ylabel("Lux")
            axs[2].grid(True)
            axs[2].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))
            for label in axs[2].get_xticklabels():
                label.set_rotation(45)
            axs[2].fill_between(x_light, y_light, y_light.min() - 1, color=color or shadow_color_2, alpha=shadow_alpha)

            axs[3].scatter(df['temperature'], df['humidity'], color=color or primary_color, s=20)
            axs[3].set_title("Humidity vs Temperature")
            axs[3].set_xlabel("Temp (°C)")
            axs[3].set_ylabel("Humidity (%)")
            axs[3].grid(True)
            for label in axs[3].get_xticklabels():
                label.set_rotation(45)

            fig.suptitle(f"Sensor Data: {title_range}", fontsize=14, fontweight='bold', y=0.995)
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
        return jsonify({"error": "Invalid date format. Use %Y-%m-%d."}), 400
