import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template
from flask_socketio import SocketIO
import socketio as sio_client
import time

BASE_URL = "http://192.168.0.47:" #Cambia a tu IP
BASE_PORT = 44111
NUM_SERVERS = 4
TEMP_PORT = 44120

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

state = {}
cpu_temp = None

def server_worker(idx, port):
    sio = sio_client.Client()

    @sio.on("new_hit")
    def on_hit():
        state[idx]["count"] += 1
        socketio.emit("update", {
            "idx": idx,
            "count": state[idx]["count"]
        })

    while True:
        try:
            sio.connect(f"{BASE_URL}{port}")
            state[idx] = {"count": 0}
            socketio.emit("init", {
                "servers": state,
                "cpu_temp": cpu_temp
            })
            sio.wait()
        except:
            state.pop(idx, None)
            socketio.emit("init", {
                "servers": state,
                "cpu_temp": cpu_temp
            })
            eventlet.sleep(2)

def temp_worker():
    sio = sio_client.Client()

    @sio.on("cpu_temp")
    def on_temp(data):
        global cpu_temp
        cpu_temp = data.get("temp")
        socketio.emit("cpu_temp", {"value": cpu_temp})

    while True:
        try:
            sio.connect(f"{BASE_URL}{TEMP_PORT}")
            sio.wait()
        except:
            eventlet.sleep(2)

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def on_connect():
    socketio.emit("init", {
        "servers": state,
        "cpu_temp": cpu_temp
    })

if __name__ == "__main__":
    for i in range(NUM_SERVERS):
        socketio.start_background_task(
            server_worker,
            i,
            BASE_PORT + i
        )

    socketio.start_background_task(temp_worker)

    socketio.run(app, host="0.0.0.0", port=50100)

