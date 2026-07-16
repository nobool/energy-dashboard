@echo off
echo ==============================================
echo I-SEM Market Dashboard - Auto Setup
echo ==============================================

IF NOT EXIST ".venv\" (
    echo Creating Python virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Starting Dashboard...
streamlit run app/Dashboard.py

pause
