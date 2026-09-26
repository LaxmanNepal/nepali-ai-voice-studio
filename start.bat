@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r backends\pocket_tts\requirements.txt
start "Nepali AI Voice Studio" cmd /k "python app.py"
timeout /t 3 /nobreak >nul
start http://127.0.0.1:7860
