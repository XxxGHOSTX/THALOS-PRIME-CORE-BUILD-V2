FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

COPY . .

# Make scripts executable
RUN chmod +x run_thalos.py quickstart.sh

# Default to CLI mode
CMD ["python3", "run_thalos.py", "--mode", "cli"]
