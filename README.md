# Probenverdünner (Raspberry Pi + Flask)

Web-gesteuerter Probenverdünner für die Uni: Flask-Webserver auf einem Raspberry Pi steuert Pumpen, Ventile und Sensoren über GPIO. Enthält eine Hardware-Abstraktionsschicht (HAL) sowie eine Mock-Implementierung für Entwicklung ohne Pi.

## Features (MVP)
- Flask-Webserver mit REST-API und einfacher Web-UI
- Hintergrund-Tasks (Start/Stop von Verdünnungsabläufen)
- HAL: `controller` Interface, `rpi_impl` (GPIO), `mock_impl` (Simulation)
- SQLite für Protokolle (später) und Basis-Konfiguration
- systemd-Unit für Autostart auf dem Raspberry Pi

## Struktur
```
app/
  __init__.py
  main.py          # App-Factory & Serverstart
  api.py           # REST-Endpoints
  templates/
    index.html     # UI
  static/
    app.js
    style.css
  hw/
    controller.py  # Interfaces
    rpi_impl.py    # GPIO-Implementation (Pi)
    mock_impl.py   # Mock für Entwicklung
  tasks/
    runner.py      # Hintergrund-Tasks
  models.py        # (später) DB-Modelle
  config.py        # Konfig
deploy/
  raspberrypi.service  # systemd Unit
scripts/
  install_pi.sh
requirements.txt
```

## Schnellstart (lokal, ohne Pi)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FLASK_ENV=development python -m app.main
```
Öffne http://localhost:5000

Mock-HAL ist Standard. Umschalten auf RPi via Environment `HW_BACKEND=rpi`.

## Deployment auf Raspberry Pi (Kurz)
```bash
git clone <repo>
cd EingebetteteSysteme_Probenverduenner_klein
bash scripts/install_pi.sh
# systemd unit anpassen & aktivieren
env HW_BACKEND=rpi python -m app.main
```

## Sicherheit
- Standardmäßig keine Auth – im Labor-Netz betreiben oder Basic-Auth / Token ergänzen.
- GPIO initialisiert sichere Zustände, Fehler stoppen Tasks.

## Nächste Schritte
- Auth / Token
- Logging in Datei + Rotierung
- Echte Sensor-/Ventilsteuerung
- Verdünnungslogik (Parametrisierte Sequenzen)

## Lizenz
MIT
