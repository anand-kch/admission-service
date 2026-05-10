FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling python packages
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# We'll use uvicorn to run the FastAPI wrapper
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]