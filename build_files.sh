#!/bin/bash
# Vercel Build Script for Grace Ville Django
echo "==> Upgrading pip..."
python3 -m pip install --upgrade pip

echo "==> Installing project requirements..."
python3 -m pip install -r requirements.txt

echo "==> Collecting static assets..."
python3 manage.py collectstatic --noinput --clear

echo "==> Grace Ville Build Successful!"

