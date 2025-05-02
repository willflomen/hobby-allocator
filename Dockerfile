FROM python:3.9-slim

WORKDIR /app

# Install system dependencies including CBC solver
RUN apt-get update && apt-get install -y \
    build-essential \
    coinor-cbc \
    glpk-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Make sure CBC is in PATH and check its availability
RUN which cbc || echo "CBC not found"
RUN pip show pulp

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the Streamlit port
EXPOSE 8501

# Command to run the app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
