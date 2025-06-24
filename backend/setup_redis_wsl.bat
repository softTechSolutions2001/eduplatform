@echo off
REM Script to set up Redis for Celery on Windows using WSL

echo ======================================================
echo Setting up Redis for Celery message broker
echo ======================================================

REM Check if WSL is installed
wsl --status > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WSL is not installed. Please install WSL by running:
    echo wsl --install
    echo Then restart your computer and run this script again.
    exit /b
)

REM Check if Ubuntu is installed
wsl -l | findstr "Ubuntu" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Ubuntu distribution not found in WSL.
    echo Installing Ubuntu...
    wsl --install -d Ubuntu
    echo Please restart your computer after Ubuntu installation completes.
    exit /b
)

REM Install Redis in WSL Ubuntu
echo Installing Redis in WSL Ubuntu...
wsl -d Ubuntu -e bash -c "sudo apt-get update && sudo apt-get install -y redis-server"

REM Configure Redis to allow remote connections
echo Configuring Redis...
wsl -d Ubuntu -e bash -c "sudo sed -i 's/bind 127.0.0.1 ::1/bind 0.0.0.0/g' /etc/redis/redis.conf"
wsl -d Ubuntu -e bash -c "sudo service redis-server restart"

REM Create startup script
echo Creating Redis startup script...
echo @echo off > start_redis.bat
echo echo Starting Redis Server using WSL... >> start_redis.bat
echo wsl -d Ubuntu -e sudo service redis-server start >> start_redis.bat
echo echo Redis started on localhost:6379 >> start_redis.bat
echo pause >> start_redis.bat

echo ======================================================
echo Redis setup complete!
echo - A start_redis.bat script has been created
echo - Run this script before starting Celery worker
echo - Redis will be available on localhost:6379
echo ======================================================

pause
