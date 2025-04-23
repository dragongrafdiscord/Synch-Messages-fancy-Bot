@echo off
setlocal

set GITHUB_URL=https://github.com/dragongrafdiscord/Synch-Messages-Bot.git
set FOLDER_NAME=Synch-Messages-Bot

echo.
echo 🔄 Cloning repository...
git clone %GITHUB_URL% %FOLDER_NAME%

cd %FOLDER_NAME%

:: Create log folders
echo 🗂️ Creating log directories...
mkdir logs
mkdir logs\archive

:: Run first-time setup
echo 🚀 Launching first_start.bat...
call first_start.bat

pause
