# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Copy backend code
COPY web/backend/ ./backend/
# Copy frontend templates
COPY web/frontend/ ./frontend/
# Copy static files
COPY web/static/ ./static/

# Create uploads directory
RUN mkdir -p ./static/uploads

# Set Python path to include the app directory
ENV PYTHONPATH=/app

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

