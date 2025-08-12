# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt /app/backend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend and ml directories
COPY backend/ /app/backend/
COPY ml/ /app/ml/

# Create uploads directory
RUN mkdir -p /app/backend/uploads

# Expose port
EXPOSE 5003

# Set Python path
ENV PYTHONPATH=/app

# Run the Flask application
CMD ["python", "backend/app_real.py"]
