FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (HF Spaces uses port 7860)
EXPOSE 7860

# Set environment variables for HF Spaces
ENV API_BASE_URL=http://localhost:7860
ENV MODEL_NAME=gpt-4o-mini
ENV HF_TOKEN=dummy

# Run the server on port 7860 for HF Spaces
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
