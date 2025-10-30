FROM python:3.11-slim

LABEL maintainer="zipline-reloaded"
LABEL description="Zipline-Reloaded with Sharadar bundle support"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    libhdf5-dev \
    pkg-config \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements*.txt pyproject.toml setup.py ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the entire project including .git for version detection
COPY . .

# Set version environment variable for setuptools-scm
ENV SETUPTOOLS_SCM_PRETEND_VERSION=3.1.1

# Install zipline-reloaded in editable mode
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /notebooks /data /root/.zipline /scripts

# Set up Jupyter
RUN pip install --no-cache-dir jupyter jupyterlab notebook

# Expose Jupyter port
EXPOSE 8888

# Set environment variables
ENV ZIPLINE_ROOT=/root/.zipline
ENV ZIPLINE_CUSTOM_DATA_DIR=/data/custom_databases
ENV PYTHONUNBUFFERED=1

# Start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
