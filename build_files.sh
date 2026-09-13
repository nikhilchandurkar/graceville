#!/bin/bash
# Vercel Build Script for Grace Ville Django
export PIP_BREAK_SYSTEM_PACKAGES=1

echo "==> Installing project requirements..."
if command -v uv &> /dev/null; then
    echo "==> Using uv for fast installation..."
    uv pip install --system -r requirements.txt || python3 -m pip install --break-system-packages -r requirements.txt
else
    python3 -m pip install --break-system-packages -r requirements.txt
fi

echo "==> Collecting static assets..."
python3 manage.py collectstatic --noinput --clear

echo "==> Grace Ville Build Successful!"
