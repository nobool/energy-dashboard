#!/bin/bash
echo "=============================================="
echo "I-SEM Market Dashboard - Auto Setup"
echo "=============================================="

if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting Dashboard..."
streamlit run app/Dashboard.py
