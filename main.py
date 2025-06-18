
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from FlightRadar24.api import FlightRadar24API
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)
fr = FlightRadar24API()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('track_flight')
def handle_track(data):
    flight_id = data.get('flight_id')
    if not flight_id:
        emit('error', {'message': 'ID du vol manquant.'})
        return

    def track():
        try:
            while True:
                flights = fr.get_flights(flight_id)
                if not flights:
                    emit('error', {'message': 'Vol non trouvé.'})
                    break
                flight = flights[0]
                trail_data = fr.get_flight_details(flight).get('trail', [])
                emit('update', {
                    'lat': getattr(flight, 'latitude', 0),
                    'lng': getattr(flight, 'longitude', 0),
                    'trail': trail_data,
                    'altitude': getattr(flight, 'altitude', 0),
                    'speed': getattr(flight, 'ground_speed', 0),
                    'callsign': getattr(flight, 'callsign', 'N/A')
                })
                socketio.sleep(5)
        except Exception as e:
            emit('error', {'message': str(e)})

    threading.Thread(target=track).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
