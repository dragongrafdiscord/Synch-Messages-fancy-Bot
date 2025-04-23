@echo off
echo 🔧 Setting up the bot environment...

:: Create log directories
mkdir logs
mkdir logs\archive

:: Install dependencies
echo 📦 Installing Python packages from requirements.txt...
pip install -r requirements.txt

echo ✅ First time setup complete.
pause
