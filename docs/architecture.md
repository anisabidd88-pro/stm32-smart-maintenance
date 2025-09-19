
# Architecture Overview

Components:
- STM32 node (simulated here by Python):
  - Reads sensors (Temp, Vibration, Sound)
  - Runs lightweight Edge AI detector (online EMA z-score)
  - Encrypts payload and sends via LoRa/WiFi to Gateway
- Gateway (server/gateway.py):
  - Receives, decrypts and stores readings into SQLite
  - Hosts a Flask dashboard (latest data + FFT)
- Digital Twin:
  - A model that mirrors machine health (see docs/ for ideas)
- Production notes:
  - Use AES-GCM, device attestation, secure boot, and a hardware secure element in production.
