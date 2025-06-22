# Multi-stage build for LAIT Legal Intelligence Platform
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Backend stage
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend
COPY --from=backend-builder /app/backend /app/backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy application files
COPY backend/ /app/backend/
COPY .env* /app/

# Create necessary directories
RUN mkdir -p /app/backend/logs /app/backend/uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/enhanced_app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/api/health || exit 1

# Start the application
CMD ["python", "backend/enhanced_app.py"]
