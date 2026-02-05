#!/bin/bash
# Setup script - creates virtual environment and installs dependencies

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "Virtual environment created at: ./venv"
echo ""
echo "To activate manually: source venv/bin/activate"
echo "To start PM2: pm2 start ecosystem.config.js"
