
#!/usr/bin/env python3
"""
sensors_sim.py
Simulates an STM32 node (sensors + simple edge AI) and sends encrypted packets to the gateway via UDP.
Run: python simulator/sensors_sim.py
"""
import socket, json, time, math, random, argparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from edge_ai import EdgeAnomalyDetector

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Demo AES key (16 bytes). CHANGE in production.
AES_KEY = b"0123456789abcdef"

def encrypt(payload_bytes):
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return cipher.encrypt(pad(payload_bytes, 16))

def generate_sample(t):
    # synthetic but realistic-ish signals
    temp = 40.0 + 2.0 * math.sin(t / 30.0) + (random.random() - 0.5) * 0.6
    vib = 0.02 + 0.01 * math.sin(t / 5.0) + (random.random() - 0.5) * 0.005
    sound = 50.0 + 3.0 * math.sin(t / 7.0) + (random.random() - 0.5) * 1.2
    return {'temp': round(temp,3), 'vib': round(vib,6), 'sound': round(sound,3)}

def main(rate_hz=1.0, node_id="node-001"):
    detector = EdgeAnomalyDetector()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Sensor simulator started - sending to {}:{}".format(UDP_IP, UDP_PORT))
    t = 0
    try:
        while True:
            sample = generate_sample(t)
            sample['timestamp'] = time.time()
            sample['node_id'] = node_id
            # run edge detector on the node (simulate STM32 Edge AI)
            score = detector.update_and_score(sample)
            sample['anomaly_score'] = score
            raw = json.dumps(sample).encode('utf-8')
            enc = encrypt(raw)
            sock.sendto(enc, (UDP_IP, UDP_PORT))
            print("SENT", sample)
            t += 1
            time.sleep(1.0 / max(rate_hz, 0.01))
    except KeyboardInterrupt:
        print("Stopped by user")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rate", type=float, default=1.0, help="samples per second")
    parser.add_argument("--node", type=str, default="node-001", help="node id")
    args = parser.parse_args()
    main(rate_hz=args.rate, node_id=args.node)
