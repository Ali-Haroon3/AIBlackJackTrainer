FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install streamlit>=1.28.0 \
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

# Create streamlit config directory
RUN mkdir -p /app/.streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]