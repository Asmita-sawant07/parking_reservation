# Use official lightweight Python base image
FROM python:3.11-slim

# Set environment variables:
# 1. PYTHONDONTWRITEBYTECODE: prevents Python from copying .pyc files into the container
# 2. PYTHONUNBUFFERED: allows instant logging of app stdout/stderr to docker logs
# 3. PORT: default port for the application
# 4. FLASK_DEBUG: ensures debug mode is disabled
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    FLASK_DEBUG=0

# Set working directory inside container
WORKDIR /app

# Copy dependency requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY app.py .

# Expose port 5000
EXPOSE 5000

# Start the Flask REST API
CMD ["python", "app.py"]
