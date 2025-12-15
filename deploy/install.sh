#!/bin/bash

# Exit on error
set -e

echo "=== Probenverdünner Installation ==="

# 1. System Updates & Dependencies
echo "[1/5] Updating system and installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git

# 2. Update Repository
echo "[2/5] Checking repository status..."
# Check if we are in a git repo
if [ -d ".git" ]; then
    echo "Git repository detected. Pulling latest changes..."
    git pull
else
    echo "Not a git repository. Skipping git pull."
fi

# 3. Python Environment Setup
echo "[3/5] Setting up Python environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "Installing Python requirements..."
pip install --upgrade pip
if [ -f "requirements-pi.txt" ]; then
    pip install -r requirements-pi.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: No requirements.txt found."
fi

# 4. Systemd Service Setup
echo "[4/5] Configuring Autostart (Systemd)..."

SERVICE_NAME="probenverduenner.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
# Always use the parent directory (project root), not deploy/
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
USER_NAME=$(whoami)

# Create service file content dynamically to match current path and user
# We use the python from the venv in project root
cat <<EOF | sudo tee $SERVICE_PATH
[Unit]
Description=Probenverduenner Webserver
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_ROOT
ExecStart=$PROJECT_ROOT/.venv/bin/python -m app.main
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
Environment=HW_BACKEND=rpi

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at $SERVICE_PATH"

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "Service enabled."

# 5. Start Service
echo "[5/5] Starting service..."
sudo systemctl restart $SERVICE_NAME

echo "=== Installation Complete ==="
echo "The webserver is now running in the background."
echo "Check status with: sudo systemctl status $SERVICE_NAME"
echo "View logs with: sudo journalctl -u $SERVICE_NAME -f"
