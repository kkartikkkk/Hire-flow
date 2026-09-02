FROM python:3.12-slim

WORKDIR /app

# Create a non-privileged system user first
RUN groupadd -g 10001 gappeo && \
    useradd -u 10001 -g gappeo -m -s /bin/bash gappeo

# Install system dependencies for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and ensure ownership
COPY . .
RUN mkdir -p /app/uploads && \
    chown -R gappeo:gappeo /app

# Expose server port and switch to the non-privileged user
EXPOSE 8000
USER gappeo

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
