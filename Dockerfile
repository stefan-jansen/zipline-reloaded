FROM python:3.11-slim

LABEL maintainer="zipline-reloaded"
LABEL description="Zipline-Reloaded with CustomData and Jupyter Notebook"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libhdf5-dev \
    libopenblas-dev \
    gfortran \
    git \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-build.txt ./

# Upgrade pip
RUN pip install --upgrade pip

# Install build dependencies
RUN pip install -r requirements-build.txt

# Install runtime dependencies
RUN pip install -r requirements.txt

# Install Jupyter and extensions
RUN pip install \
    jupyter \
    jupyterlab \
    notebook \
    ipywidgets \
    jupyter_contrib_nbextensions \
    matplotlib \
    seaborn \
    plotly \
    pandas-datareader

# Copy the entire project
COPY . .

# Install zipline-reloaded in editable mode
# Set version for setuptools-scm (git metadata not available in Docker build)
ENV SETUPTOOLS_SCM_PRETEND_VERSION=3.0.4
RUN pip install -e .

# Create directories for data and notebooks
RUN mkdir -p /data/custom_databases \
    && mkdir -p /notebooks \
    && mkdir -p /root/.zipline/custom_data

# Set environment variables
ENV ZIPLINE_ROOT=/root/.zipline
ENV ZIPLINE_CUSTOM_DATA_DIR=/data/custom_databases
ENV PYTHONUNBUFFERED=1

# Copy example notebooks
COPY notebooks/ /notebooks/

# Expose Jupyter port
EXPOSE 8888

# Configure Jupyter to allow connections from any IP
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> /root/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> /root/.jupyter/jupyter_notebook_config.py

# Set working directory to notebooks
WORKDIR /notebooks

# Default command: start Jupyter Lab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
