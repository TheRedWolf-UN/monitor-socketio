from flask import Flask
from flask_socketio import SocketIO
import os
import time

LOG_FILE = "tarea1.txt" # Cambia a la ruta de tu archivo

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def watch_log():
    try:
        last_mtime = os.path.getmtime(LOG_FILE)
    except:
        last_mtime = 0

    while True:
        try:
            mtime = os.path.getmtime(LOG_FILE)
            if mtime != last_mtime:
                last_mtime = mtime
                socketio.emit("new_hit")
                print (f"New hit ...")
        except:
            pass

        socketio.sleep(0.1)

@socketio.on("connect")
def connect():
    print("cliente conectado")

if __name__ == "__main__":
    print ( f"Iniciando servidor ..." )
    socketio.start_background_task(watch_log)
    socketio.run(app, host="0.0.0.0", port=44111)
