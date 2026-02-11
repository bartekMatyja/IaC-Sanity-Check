FROM python:3.10-slim

# Install system dependencies if needed (e.g. git for checkov to scan git repos)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Compile to bytecode (legacy mode to keep .pyc next to .py)
RUN python -m compileall -b . && \
    find . -name "*.py" -delete

# Set the entrypoint to run the compiled main script
ENTRYPOINT ["python", "/app/main.pyc"]
