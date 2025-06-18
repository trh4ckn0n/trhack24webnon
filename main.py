from flask import Flask, render_template, request
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# On force 'threading' comme mode async pour éviter eventlet/green issues
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

def background_task(sid, data):
    try:
        for i in range(5):
            time.sleep(1)
            socketio.emit('progress', {'count': i+1}, namespace='/', to=sid)
        socketio.emit('done', {'message': 'Tâche terminée !'}, namespace='/', to=sid)
    except Exception as e:
        socketio.emit('error', {'message': str(e)}, namespace='/', to=sid)

@socketio.on('start_task')
def handle_start_task(data):
    sid = request.sid  # Identifiant du client connecté
    thread = threading.Thread(target=background_task, args=(sid, data))
    thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=False, host="0.0.0.0")
