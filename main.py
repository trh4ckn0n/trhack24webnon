# main.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

def recherche_vols(params, sid):
    # Simule une recherche avec progression
    for i in range(1, 6):
        time.sleep(1)
        socketio.emit('progress', {'step': i, 'msg': f'Progression: {i}/5'}, to=sid)
    # Résultat simulé
    vols = [
        {"vol": "AF123", "depart": params.get("depart"), "arrivee": params.get("arrivee"), "prix": "150€"},
        {"vol": "BA456", "depart": params.get("depart"), "arrivee": params.get("arrivee"), "prix": "200€"},
    ]
    socketio.emit('result', {'vols': vols}, to=sid)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_search')
def start_search(data):
    sid = request.sid
    threading.Thread(target=recherche_vols, args=(data, sid)).start()
    emit('started', {'msg': 'Recherche démarrée...'})

if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0")
