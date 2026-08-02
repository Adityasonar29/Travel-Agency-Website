#!/bin/bash

echo "Building project..."
# Add the --break-system-packages flag to bypass PEP 668 restriction
python3 -m pip install -r requirements.txt --break-system-packages

echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear
