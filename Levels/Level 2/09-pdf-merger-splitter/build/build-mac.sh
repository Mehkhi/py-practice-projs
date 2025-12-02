#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --upgrade pip
python3 -m pip install -r ../requirements.txt

pyinstaller --noconfirm build/pdf_split.spec

echo "App built at dist/PDF Split.app"
