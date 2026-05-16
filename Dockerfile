# Dockerfile — Mock CPE Flask Application
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create runtime directories
RUN mkdir -p /app/data /app/reports /app/allure-results /app/screenshots

EXPOSE 5000

# Bind to 0.0.0.0 for Docker network accessibility
CMD ["python", "run.py"]
