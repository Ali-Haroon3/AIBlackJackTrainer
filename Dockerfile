FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install flask>=3.0.0 \
                flask-socketio>=5.3.0 \
                flask-cors>=4.0.0 \
                pandas>=1.5.0 \
                numpy>=1.24.0 \
                plotly>=5.15.0 \
                scikit-learn>=1.3.0 \
                requests>=2.31.0 \
                beautifulsoup4>=4.12.0 \
                trafilatura>=1.6.0 \
                Pillow>=10.0.0 \
                sqlalchemy>=2.0.0 \
                psycopg2-binary>=2.9.0 \
                python-dotenv>=1.0.0

# Copy application code
COPY . .

# Expose port 8080 for AWS load balancer
EXPOSE 8080

# Health check for AWS load balancer
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8080/health || exit 1

# Run Flask application
CMD ["python", "flask_app.py"]