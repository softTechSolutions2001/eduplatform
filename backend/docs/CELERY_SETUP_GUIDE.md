# Celery Setup Guide for AI Course Builder

This guide explains how to set up and run the Celery worker for the AI Course Builder async tasks.

## Prerequisites

1. Redis server (message broker)
2. Python virtual environment with required packages

## Setup Steps

### 1. Install Redis

#### For Windows:

Use the provided script that sets up Redis in WSL (Windows Subsystem for Linux):

```bash
# Run the setup script
backend\setup_redis_wsl.bat
```

This will:
- Install Redis in WSL Ubuntu
- Configure Redis for remote connections
- Create a start_redis.bat script

#### For macOS:

```bash
# Install Redis using Homebrew
brew install redis

# Start Redis
brew services start redis
```

#### For Linux:

```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Enable and start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Install Python Dependencies

```bash
# Activate your virtual environment
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install Celery and Redis dependencies
pip install -r requirements-celery.txt
```

### 3. Start the Celery Worker

```bash
# Make sure Redis is running first
# Then start the Celery worker
cd backend
start_celery.bat  # Windows
# OR
celery -A educore worker --loglevel=INFO  # macOS/Linux
```

### 4. Optional: Start Flower Monitoring (if installed)

```bash
# In a separate terminal
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

celery -A educore flower --port=5555
```

Then access the Flower dashboard at http://localhost:5555

## Troubleshooting

### Redis Connection Issues

If Celery cannot connect to Redis, check if:

1. Redis is running: `redis-cli ping` should return "PONG"
2. Redis is accessible on localhost:6379
3. CELERY_BROKER_URL is correctly set in settings.py

### Task Execution Issues

1. Check celery logs for error messages
2. Verify task registration in the Celery app
3. Ensure the task has enough time before hitting soft/hard time limits

## Production Considerations

For production deployments:

1. Use a dedicated Redis instance with password protection
2. Configure appropriate Celery worker concurrency based on server resources
3. Set up monitoring with Flower or other tools
4. Consider using supervisord or systemd to manage Celery workers
