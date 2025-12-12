#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -eq 0 ]]; then
  echo "Bitte nicht als root ausführen (sudo wird intern verwendet)." >&2
fi

sudo apt-get update
sudo apt-get install -y python3-venv python3-pip git

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Installation abgeschlossen. Start mit: python -m app.main" 
