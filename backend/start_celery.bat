@echo off
REM Start Celery worker for AI Course Builder tasks
cd %~dp0

echo Starting Celery worker for eduplatform...
echo Make sure Redis server is running on localhost:6379

REM Activate virtual environment
call venv\scripts\activate

REM Start Celery worker with concurrency=2 (can adjust based on CPU cores)
celery -A educore worker --loglevel=INFO --concurrency=2 -n ai_builder_worker@%%h

REM If you want to monitor tasks with Flower, uncomment the next line
REM start cmd /k "celery -A educore flower --port=5555"
