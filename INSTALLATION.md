# Installation Guide for Zipline-Reloaded

This guide covers different ways to install and set up zipline-reloaded with the new CustomData functionality.

## Table of Contents

1. [Quick Installation](#quick-installation)
2. [Development Installation](#development-installation)
3. [Platform-Specific Notes](#platform-specific-notes)
4. [Troubleshooting](#troubleshooting)
5. [Verifying Installation](#verifying-installation)

---

## Quick Installation

### Prerequisites

- **Python**: 3.9, 3.10, 3.11, or 3.12
- **Operating System**: Linux, macOS, or Windows
- **Recommended**: Use a virtual environment (conda or venv)

### Option 1: Using pip (Recommended)

```bash
# Create and activate virtual environment
python -m venv zipline-env
source zipline-env/bin/activate  # On Windows: zipline-env\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install build dependencies first
pip install -r requirements-build.txt

# Install zipline-reloaded
pip install -e .

# Or install with all dependencies from requirements
pip install -r requirements.txt
```

### Option 2: Using conda (Alternative)

```bash
# Create conda environment
conda create -n zipline python=3.11
conda activate zipline

# Install build dependencies
pip install -r requirements-build.txt

# Install zipline-reloaded
pip install -e .
```

---

## Development Installation

For contributing to zipline-reloaded or testing the CustomData functionality:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/stefan-jansen/zipline-reloaded.git
cd zipline-reloaded

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install build dependencies
pip install -r requirements-build.txt

# Install in editable mode with all dev dependencies
pip install -r requirements-dev.txt
pip install -e .

# Run tests to verify
pytest tests/
```

---

## Platform-Specific Notes

### Linux

**Ubuntu/Debian:**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    libhdf5-dev \
    libatlas-base-dev \
    gfortran

# Then follow standard installation
pip install -r requirements-build.txt
pip install -e .
```

**Fedora/RHEL/CentOS:**
```bash
# Install system dependencies
sudo dnf install -y \
    gcc \
    gcc-c++ \
    python3-devel \
    hdf5-devel \
    atlas-devel \
    gcc-gfortran

# Then follow standard installation
pip install -r requirements-build.txt
pip install -e .
```

### macOS

**Using Homebrew:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install hdf5 c-blosc

# Set environment variables for HDF5
export HDF5_DIR=/opt/homebrew/opt/hdf5  # For Apple Silicon
# or
export HDF5_DIR=/usr/local/opt/hdf5     # For Intel

# Install zipline-reloaded
pip install -r requirements-build.txt
pip install -e .
```

**Apple Silicon (M1/M2/M3) Note:**
- Some packages may need to be built from source
- Use Python 3.10+ for better ARM compatibility
- Consider using conda-forge for pre-built packages

### Windows

**Prerequisites:**
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022)
- Or install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

```powershell
# In PowerShell or Command Prompt

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install build dependencies
pip install -r requirements-build.txt

# Install zipline-reloaded
pip install -e .
```

**Common Windows Issues:**
- If you encounter "error: Microsoft Visual C++ 14.0 is required", install Visual C++ Build Tools
- For HDF5/tables issues, try: `pip install tables --no-binary tables`

---

## Troubleshooting

### Issue: NumPy Version Conflicts

**Problem:** NumPy 2.0 compatibility issues

**Solution:**
```bash
# For Python 3.9
pip install "numpy>=1.23.5,<2.0"

# For Python 3.10-3.11
pip install "numpy>=1.23.5,<2.0"

# For Python 3.12
pip install "numpy>=1.26.0"
```

### Issue: Cython Compilation Errors

**Problem:** "Cython is not installed" or compilation fails

**Solution:**
```bash
# Install Cython first
pip install "Cython>=0.29.21,<3.0"

# Clean previous build artifacts
python setup.py clean --all
rm -rf build/ dist/ *.egg-info

# Rebuild
pip install -e .
```

### Issue: HDF5/tables Installation Fails

**Problem:** h5py or tables won't install

**Solutions:**

**Linux:**
```bash
sudo apt-get install libhdf5-dev  # Ubuntu/Debian
sudo dnf install hdf5-devel       # Fedora/RHEL
```

**macOS:**
```bash
brew install hdf5
export HDF5_DIR=$(brew --prefix hdf5)
pip install h5py tables --no-binary :all:
```

**Windows:**
```bash
# Try pre-built wheels
pip install --only-binary :all: h5py tables
```

### Issue: bcolz-zipline Installation Fails

**Problem:** bcolz-zipline compilation errors

**Solution:**
```bash
# Install NumPy first
pip install "numpy<2.0"

# Then install bcolz-zipline
pip install bcolz-zipline
```

### Issue: TA-Lib Installation (Optional)

**Problem:** TA-Lib is optional but useful for technical indicators

**Solutions:**

**Linux:**
```bash
# Install TA-Lib C library
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install ta-lib
```

**macOS:**
```bash
brew install ta-lib
pip install ta-lib
```

**Windows:**
- Download TA-Lib from: https://github.com/cgohlke/talib-build/releases
- Install the wheel: `pip install TA_Lib‑0.4.xx‑cpxx‑cpxx‑win_amd64.whl`

---

## Verifying Installation

### 1. Check Installation

```bash
# Verify zipline is installed
python -c "import zipline; print(zipline.__version__)"

# Check CustomData functionality
python -c "from zipline.pipeline.data import CustomData; print('CustomData OK')"

# Check database functionality
python -c "from zipline.pipeline.data import create_custom_db; print('Database OK')"
```

### 2. Run Quick Test

```python
# test_install.py
from zipline.pipeline.data import CustomData
from zipline.pipeline import Pipeline
import numpy as np

# Create a simple custom dataset
TestData = CustomData(
    'TestData',
    columns={'metric': float}
)

# Create a pipeline
pipe = Pipeline(
    columns={'test': TestData.metric.latest}
)

print("✓ CustomData successfully imported and tested")
print(f"✓ Dataset: {TestData}")
print(f"✓ Column: {TestData.metric}")
print("✓ Installation verified!")
```

Run it:
```bash
python test_install.py
```

### 3. Run Examples

```bash
# Test in-memory CustomData
python examples/custom_data_example.py

# Test database CustomData
python examples/custom_data_database_example.py
```

### 4. Run Unit Tests

```bash
# Run all tests
pytest tests/

# Run CustomData-specific tests
pytest tests/pipeline/test_custom_data.py -v
pytest tests/pipeline/test_custom_db.py -v

# Run with coverage
pytest tests/ --cov=zipline --cov-report=html
```

---

## Minimal Installation (Runtime Only)

If you only need to run zipline (not develop it):

```bash
# Create environment
python -m venv zipline-env
source zipline-env/bin/activate

# Install only runtime dependencies
pip install -r requirements.txt

# Install zipline-reloaded
pip install -e .
```

---

## Docker Installation (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libhdf5-dev \
    libatlas-base-dev \
    gfortran \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements*.txt ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements-build.txt && \
    pip install -r requirements.txt

# Copy source code
COPY . .

# Install zipline-reloaded
RUN pip install -e .

# Run tests to verify
RUN pytest tests/pipeline/test_custom_data.py -v

CMD ["python"]
```

Build and run:
```bash
docker build -t zipline-reloaded .
docker run -it zipline-reloaded python
```

---

## Environment Variables

Optional environment variables you can set:

```bash
# Database directory for CustomData
export ZIPLINE_CUSTOM_DATA_DIR="/path/to/custom/data"

# Default data bundle
export ZIPLINE_ROOT="~/.zipline"

# Matplotlib backend (for headless servers)
export MPLBACKEND="Agg"
```

---

## Next Steps

After successful installation:

1. **Read the documentation:**
   - [CustomData User Guide](docs/CUSTOM_DATA.md)
   - [Database Storage Guide](docs/CUSTOM_DATA_DATABASE.md)

2. **Try the examples:**
   - `examples/custom_data_example.py`
   - `examples/custom_data_database_example.py`

3. **Start developing:**
   ```python
   from zipline.pipeline.data import CustomData, create_custom_db

   # Your custom trading strategy here!
   ```

---

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Search [GitHub Issues](https://github.com/stefan-jansen/zipline-reloaded/issues)
3. Review the [documentation](https://zipline.ml4trading.io)
4. Ask in the community forums

---

## Summary of Requirements Files

- **`requirements.txt`** - Core runtime dependencies (minimal for running)
- **`requirements-build.txt`** - Build dependencies (needed for installation)
- **`requirements-test.txt`** - Testing dependencies (for running tests)
- **`requirements-dev.txt`** - All dependencies (for development)

**Quick installation command:**
```bash
pip install -r requirements-build.txt && pip install -e .
```

**Full development setup:**
```bash
pip install -r requirements-dev.txt && pip install -e .
```
