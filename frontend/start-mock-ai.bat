@echo off
echo Starting AI Course Builder in Mock Mode...
echo.
echo This script will start the frontend with mock AI responses enabled
echo No backend or API keys required
echo.

cd %~dp0
call npm run dev:mock

pause
