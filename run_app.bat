@echo off
echo 🚀 Starting ResumeAI Pro - Complete SaaS Version
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
pip install -r requirements_phase3.txt

echo 🧠 Downloading NLP model...
python -m spacy download en_core_web_sm

echo 🎯 Launching ResumeAI Pro...
echo.
echo 🌐 Your app will open at: http://localhost:8501
echo 📱 Features available:
echo   ✅ User Authentication
echo   ✅ Resume Analysis & Rewriting
echo   ✅ AI Cover Letter Generator
echo   ✅ Interview Question Prep
echo   ✅ Professional PDF Reports
echo   ✅ Analysis History
echo.

streamlit run phase3_app.py

pause