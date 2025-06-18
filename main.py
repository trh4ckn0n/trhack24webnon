from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from FlightRadar24.api import FlightRadar24API
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")
fr = FlightRadar24API()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/countries')
def countries():
    airports = fr.get_airports()
    countries = sorted({getattr(a, "country", "") for a in airports})
    return jsonify(countries)

@app.route('/airports', methods=['POST'])
def airports():
    country = request.json.get('country')
    airports = fr.get_airports()
    return jsonify([
        {"icao": getattr(a, "icao", ""),
         "name": getattr(a, "name", "")}
        for a in airports if getattr(a, "country", "") == country
    ])

@app.route('/flights', methods=['POST'])
def flights():
    airport = request.json.get('icao')
    flights = fr.get_flights(airport)
    return jsonify([
        {"id": getattr(f, "id", ""),
         "callsign": getattr(f, "callsign", ""),
         "origin": getattr(f, "origin_airport_icao", "??"),
         "destination": getattr(f, "destination_airport_icao", "??")}
        for f in flights
    ])

@socketio.on('track')
def handle_track(data):
    flight_id = data.get('flight_id')
    sid = request.sid
    def track_loop():
        while True:
            try:
                flight = fr.get_flight(flight_id) or None
                details = fr.get_flight_details(flight or flight_id)
                if not details:
                    socketio.emit('error', {"msg": "Données introuvables"}, to=sid)
                    break
                last = details.get("trail", [{}])[-1]
                socketio.emit('position', {
                    "lat": last.get("lat", 0),
                    "lng": last.get("lng", 0),
                    "alt": last.get("altitude", 0),
                    "spd": last.get("groundspeed", 0)
                }, to=sid)
                time.sleep(5)
            except Exception as e:
                socketio.emit('error', {"msg": str(e)}, to=sid)
                break
    threading.Thread(target=track_loop, daemon=True).start()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
