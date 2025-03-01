# Use Python 3.9 slim image with nginx
FROM python:3.9-slim

# Install nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy nginx configuration
RUN echo 'server { \
    listen 8080; \
    location / { \
        root /app; \
        index test.html; \
    } \
    location /webhook { \
        proxy_pass http://127.0.0.1:5000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/sites-enabled/default

# Set environment variables
ENV PORT=8080

# Start both nginx and Flask app
CMD service nginx start && python webhook_listener.py
