"""
Dockerfile for Boliganalyseverktøy web application

This Dockerfile sets up the environment for running the Boliganalyseverktøy web application.
"""

FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p .streamlit data/cache

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["streamlit", "run", "ui/web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
