
# Smart Predictive Maintenance System (IoT + STM32) — Expert Demo

A complete **expert-level** project scaffold that you can download and run on your PC to simulate an STM32-based predictive maintenance system.

It contains:
- A *sensor + edge node* simulator (Python) that mimics an STM32 node (sensors: temperature, vibration, sound), runs edge AI, and sends encrypted packets to a gateway.
- A *gateway + dashboard* (Flask) that receives data, stores it in SQLite, and shows an interactive dashboard (health score, recent readings, FFT endpoint).
- A *digital twin* example and an STM32 firmware template (well-documented) to port to real hardware.
- Security demo (AES encryption for transport) and instructions for production hardening.

## Contents
- `simulator/` — sensor & edge node simulator (Python)
- `server/` — UDP gateway + Flask dashboard
- `stm32_firmware/` — STM32CubeIDE-friendly firmware skeleton and guidance
- `docs/` — architecture, run instructions, testing guidance
- `requirements.txt` — Python dependencies
- `run_all.sh` — convenience script to run the demo services locally

## Quick start (Linux / macOS / WSL)
1. Create a virtualenv and install deps:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the server/gateway (this will start UDP listener + Flask web dashboard on http://127.0.0.1:8080):
   ```bash
   python server/gateway.py
   ```
3. In a separate terminal (with the same venv), run the sensor + edge simulator:
   ```bash
   python simulator/sensors_sim.py
   ```
4. Open the dashboard: http://127.0.0.1:8080 — you will see live updates, health score and links to FFT and raw log.

## Notes / Next steps for production
- The AES demo uses a static key for simplicity. In production use a secure key store or hardware secure element (ATECC608A or similar) and use authenticated encryption (AES-GCM).
- The STM32 template shows HAL/I2C/ADC and SX127x (LoRa) integration points but you must adapt pinouts and drivers for your board.
- For on-device TinyML consider converting a trained TensorFlow Lite model; this demo uses an explainable, online anomaly detector (robust and lightweight).

---

**Arabic note (ملاحظة بالعربية):** هذا المشروع جاهز للتنفيذ والمحاكاة على الحاسوب. قمت بإضافة قالب للـSTM32 مع تعليمات لبنائه على جهازك. إذا أردت، أستطيع لاحقًا توليد مشروع STM32CubeMX/STM32CubeIDE مبدأي (بحاجة لبيانات لوحة التطوير الخاصة بك: الـMCU، الـperipherals، والـpins).
