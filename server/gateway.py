
#!/usr/bin/env python3
"""
gateway.py
- UDP listener that accepts encrypted packets from simulated nodes
- Decrypts, stores into SQLite, updates in-memory latest state
- Runs a Flask dashboard showing latest readings and simple health score.
"""
import socket, threading, time, json, sqlite3, os
from flask import Flask, jsonify, render_template, send_file, Response
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import io, numpy as np, matplotlib.pyplot as plt
from collections import deque

# Same AES key as simulator (demo only)
AES_KEY = b"0123456789abcdef"
UDP_LISTEN_IP = "0.0.0.0"
UDP_LISTEN_PORT = 5005

DB_PATH = os.path.join(os.path.dirname(__file__), "gateway_data.db")

# in-memory store: keep last N values per node
LATEST = {}
HISTORY = {}  # node_id -> deque of recent samples (vibration for FFT)
HISTORY_MAX = 1024

def decrypt(data):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    raw = unpad(cipher.decrypt(data), 16)
    return raw

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT,
            ts REAL,
            temp REAL,
            vib REAL,
            sound REAL,
            anomaly_score REAL
        )
    """)
    conn.commit()
    conn.close()

def save_reading(sample):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO readings (node_id, ts, temp, vib, sound, anomaly_score) VALUES (?,?,?,?,?,?)',
              (sample.get('node_id'), sample.get('timestamp'), sample.get('temp'), sample.get('vib'), sample.get('sound'), sample.get('anomaly_score')))
    conn.commit()
    conn.close()

def udp_listener(stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
    print("UDP listener bound to {}:{}".format(UDP_LISTEN_IP, UDP_LISTEN_PORT))
    while not stop_event.is_set():
        data, addr = sock.recvfrom(4096)
        try:
            raw = decrypt(data)
            sample = json.loads(raw.decode('utf-8'))
            node = sample.get('node_id', 'unknown')
            LATEST[node] = sample
            if node not in HISTORY:
                HISTORY[node] = deque(maxlen=HISTORY_MAX)
            HISTORY[node].append(sample)
            save_reading(sample)
            print("RECV from {}: {}".format(addr, sample))
        except Exception as e:
            print("Failed to parse packet:", e)

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    # show latest readings in JSON + a simple health score
    nodes = []
    for node, s in LATEST.items():
        nodes.append({
            'node_id': node,
            'latest': s
        })
    return render_template("index.html", nodes=nodes)

@app.route("/api/latest")
def api_latest():
    return jsonify(LATEST)

@app.route("/fft/<node_id>.png")
def fft_png(node_id):
    # generate FFT plot for last vibration samples
    if node_id not in HISTORY or len(HISTORY[node_id]) < 8:
        return "not enough data", 404
    vib = np.array([s['vib'] for s in HISTORY[node_id]])
    # basic detrend
    vib = vib - np.mean(vib)
    N = len(vib)
    freqs = np.fft.rfftfreq(N, d=1.0)
    spec = np.abs(np.fft.rfft(vib))
    fig, ax = plt.subplots()
    ax.plot(freqs, spec)
    ax.set_xlabel("Hz")
    ax.set_ylabel("magnitude")
    ax.set_title("Vibration spectrum for {}".format(node_id))
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

def start_flask():
    app.run(host="127.0.0.1", port=8080, debug=False, use_reloader=False)

def main():
    init_db()
    stop_event = threading.Event()
    t = threading.Thread(target=udp_listener, args=(stop_event,), daemon=True)
    t.start()
    print("Starting Flask dashboard on http://127.0.0.1:8080")
    start_flask()
    stop_event.set()

if __name__ == "__main__":
    main()
