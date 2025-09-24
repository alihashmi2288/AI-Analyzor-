@echo off
echo 🚀 Starting Clean AI Resume Analyzer...
echo.
echo ✅ Installing dependencies...
pip install streamlit pdfplumber docx2txt scikit-learn google-generativeai plotly > nul 2>&1
echo.
echo 🎯 Launching AI Resume Analyzer...
echo 📱 Opening at: http://localhost:8501
echo.
python -m streamlit run clean_app.py
pause