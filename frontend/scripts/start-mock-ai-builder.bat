@echo off
echo Starting AI Course Builder with mock responses...

:: Set environment variables for mock mode
set VITE_MOCK_AI=true
set VITE_AI_MOCK_RESPONSES=true
set VITE_AI_DEBUG_MODE=true

:: Start the frontend with the environment variables
cd %~dp0..
echo Starting development server with mock API...
npm run dev
