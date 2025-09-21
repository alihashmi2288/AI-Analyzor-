import subprocess
import sys

try:
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")