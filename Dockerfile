# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY LICENSE .
COPY README.md .

# Create necessary directories
RUN mkdir -p /app/docs /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Cloud Run expects the service to listen on PORT
EXPOSE 8080

# Use the FastAPI app for Cloud Run (HTTP interface)
CMD ["python", "src/main.py"]