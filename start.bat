@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Failed to create the virtual environment.
    pause
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"

echo Updating pip...
python -m pip install --upgrade pip
if errorlevel 1 (
  echo pip upgrade failed.
  pause
  exit /b 1
)

echo Installing shared dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Shared dependency installation failed.
  pause
  exit /b 1
)

echo Installing Pocket-TTS backend dependencies...
python -m pip install -r backends\pocket_tts\requirements.txt
if errorlevel 1 (
  echo Pocket-TTS dependency installation failed.
  pause
  exit /b 1
)

echo Verifying PyTorch...
python -c "import torch; print('PyTorch', torch.__version__, '| CUDA:', torch.cuda.is_available())"
if errorlevel 1 (
  echo PyTorch is not installed correctly.
  echo Run this file again after checking the Python installation.
  pause
  exit /b 1
)

echo Starting Nepali AI Voice Studio...
start "Nepali AI Voice Studio" cmd /k "cd /d ""%~dp0"" && call "".venv\Scripts\activate.bat"" && python app.py"
timeout /t 3 /nobreak >nul
start http://127.0.0.1:7860
