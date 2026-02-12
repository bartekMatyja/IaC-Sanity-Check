FROM python:3.10-slim

# Install system dependencies if needed (e.g. git for checkov to scan git repos)
# Install system dependencies
# git: for checkov
# curl: for installing trivy/gitleaks
RUN apt-get update && apt-get install -y git curl tar && rm -rf /var/lib/apt/lists/*

# Install Gitleaks
RUN curl -L https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz -o gitleaks.tar.gz && \
    tar -xzf gitleaks.tar.gz && \
    mv gitleaks /usr/local/bin/ && \
    rm gitleaks.tar.gz

# Install Trivy
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

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
