# Zipline-Reloaded Docker + Jupyter Setup

Complete Docker setup for running zipline-reloaded with Jupyter notebooks and CustomData functionality.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up -d

# Access Jupyter Lab in your browser
open http://localhost:9000

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Option 2: Using Docker directly

```bash
# Build the image
docker build -t zipline-reloaded:latest .

# Run the container
docker run -d \
  -p 9000:8888 \
  -v $(pwd)/notebooks:/notebooks \
  -v $(pwd)/data:/data \
  --name zipline-jupyter \
  zipline-reloaded:latest

# Access Jupyter Lab
open http://localhost:9000

# View logs
docker logs -f zipline-jupyter

# Stop the container
docker stop zipline-jupyter
docker rm zipline-jupyter
```

## What's Included

- **Python 3.11** with zipline-reloaded
- **Jupyter Lab** for interactive development
- **CustomData functionality** with database persistence
- **Data Bundle System** for persistent backtesting data
- **Example notebooks** demonstrating usage
- **Data persistence** via Docker volumes
- **Management scripts** for bundle operations
- **Pre-installed packages**:
  - numpy, pandas, scipy
  - matplotlib, seaborn, plotly
  - yfinance, nasdaq-data-link
  - zipline-reloaded with all dependencies
  - jupyterlab extensions

## 📦 Using Data Bundles in Docker

Zipline bundles provide persistent, optimized storage for backtesting. All bundle data is stored in a Docker volume and persists across container restarts.

### Quick Start with Bundles

```bash
# Setup Yahoo Finance bundle (free)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Setup NASDAQ bundle (requires API key in .env)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset EOD

# List available bundles
docker exec -it zipline-reloaded-jupyter zipline bundles

# Update bundles with latest data
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --all
```

### Bundle Storage

Bundles are stored in the `zipline-data` Docker volume:
- **Path in container**: `/root/.zipline/`
- **Persistent**: Survives container restarts
- **Format**: bcolz (optimized for backtesting)

### API Keys for NASDAQ

Edit `.env` file:
```bash
cp .env.example .env
# Add your key:
echo "NASDAQ_DATA_LINK_API_KEY=your_key_here" >> .env

# Restart container
docker-compose restart
```

### Run Backtests Using Bundles

```python
# In Jupyter notebook
from zipline import run_algorithm
import pandas as pd

results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='yahoo',  # Uses persistent bundle data!
)
```

**📖 Complete Docker bundle guide**: [docs/DOCKER_BUNDLES.md](docs/DOCKER_BUNDLES.md)

## Directory Structure

```
zipline-reloaded/
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Docker Compose configuration
├── .env.example           # Environment variables template
├── .env                   # Your API keys (create from .env.example)
├── notebooks/             # Jupyter notebooks (mounted, persistent)
│   ├── 01_customdata_quickstart.ipynb
│   ├── 02_database_storage.ipynb
│   ├── 03_market_data_example.ipynb
│   ├── 04_nasdaq_datalink_example.ipynb
│   ├── 05_backtesting_with_bundles.ipynb
│   └── ... your notebooks
├── scripts/               # Management scripts (mounted)
│   └── manage_data.py     # Bundle management tool
├── data/                  # Persistent data (mounted)
│   └── custom_databases/  # SQLite databases for CustomData
├── zipline-data/          # Docker volume for bundles (persistent)
│   └── [bundle-name]/     # Bundle data in bcolz format
└── README_DOCKER.md       # This file
```

## Accessing Jupyter

After starting the container:

1. **Open your browser** to http://localhost:9000
2. **No password required** (configured for local development)
3. **Notebooks** are in the `/notebooks` directory
4. **Data** persists in `/data` directory

## Working with Notebooks

### Create a New Notebook

1. Click "+" in Jupyter Lab
2. Select "Python 3" kernel
3. Start coding!

```python
from zipline.pipeline.data import CustomData
from zipline.pipeline import Pipeline

# Your code here...
```

### Run Example Notebooks

Pre-loaded notebooks demonstrate:

1. **`01_customdata_quickstart.ipynb`** (Beginner)
   - Creating custom datasets
   - Building pipelines
   - Visualizing data

2. **`02_database_storage.ipynb`** (Intermediate)
   - Persistent database storage
   - Querying data efficiently
   - Managing multiple databases

3. **`03_market_data_example.ipynb`** (Advanced)
   - Fetching real market data from Yahoo Finance
   - Building pipelines with live data
   - Technical analysis and visualizations

4. **`04_nasdaq_datalink_example.ipynb`** (Professional)
   - Professional-grade NASDAQ Data Link integration
   - API key setup and configuration
   - Premium EOD and free WIKI datasets

5. **`05_backtesting_with_bundles.ipynb`** (Essential)
   - Setting up persistent data bundles
   - Running backtests with `run_algorithm()`
   - Daily data updates and automation

## Data Persistence

Data is persisted using Docker volumes:

### Named Volume (default)
```yaml
volumes:
  zipline-data:  # Managed by Docker
```

View volume contents:
```bash
docker volume inspect zipline-reloaded_zipline-data
```

### Host Directory Mounting
Edit `docker-compose.yml`:
```yaml
volumes:
  - ./notebooks:/notebooks     # Your notebooks
  - ./data:/data              # Your data
  - ./zipline-data:/root/.zipline  # Host directory
```

## Customization

### Change Jupyter Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "9999:8888"  # Access on port 9999
```

### Set Jupyter Password

1. Generate password hash:
```bash
docker run -it zipline-reloaded:latest python -c \
  "from notebook.auth import passwd; print(passwd())"
```

2. Edit Dockerfile:
```dockerfile
RUN echo "c.NotebookApp.password = 'sha1:...'" >> /root/.jupyter/jupyter_notebook_config.py
```

3. Rebuild:
```bash
docker-compose build
```

### Install Additional Packages

Edit `Dockerfile` and add:
```dockerfile
RUN pip install \
    your-package-1 \
    your-package-2
```

Then rebuild:
```bash
docker-compose build
```

Or install at runtime:
```bash
docker exec -it zipline-reloaded-jupyter pip install your-package
```

## Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env`:
```
JUPYTER_PORT=9000
JUPYTER_TOKEN=your-secret-token
ZIPLINE_ROOT=/root/.zipline
ZIPLINE_CUSTOM_DATA_DIR=/data/custom_databases
```

## Troubleshooting

### Container won't start

Check logs:
```bash
docker-compose logs
```

### Jupyter not accessible

1. Check if container is running:
```bash
docker ps
```

2. Check port mapping:
```bash
docker port zipline-reloaded-jupyter
```

3. Try localhost instead of 0.0.0.0:
```
http://127.0.0.1:9000
```

### Out of memory

Increase Docker memory limit:
- Docker Desktop → Preferences → Resources → Memory
- Increase to 4GB or more

### Notebooks not saving

Check volume mounts:
```bash
docker inspect zipline-reloaded-jupyter | grep Mounts -A 20
```

Ensure `./notebooks` directory exists and has write permissions.

### Database permission errors

Fix permissions:
```bash
chmod -R 755 ./data
```

## Advanced Usage

### Run Python Scripts

Execute scripts in the container:
```bash
docker exec -it zipline-reloaded-jupyter python /app/examples/custom_data_example.py
```

### Access Container Shell

```bash
docker exec -it zipline-reloaded-jupyter bash
```

### Run Tests

```bash
docker exec -it zipline-reloaded-jupyter pytest tests/pipeline/test_custom_data.py -v
```

### Create Database Backups

```bash
# Backup all databases
docker exec zipline-reloaded-jupyter tar -czf /tmp/backup.tar.gz /data/custom_databases

# Copy to host
docker cp zipline-reloaded-jupyter:/tmp/backup.tar.gz ./backup.tar.gz
```

### Restore Database Backups

```bash
# Copy backup to container
docker cp ./backup.tar.gz zipline-reloaded-jupyter:/tmp/

# Extract
docker exec zipline-reloaded-jupyter tar -xzf /tmp/backup.tar.gz -C /
```

## Using with VS Code

### Remote Containers Extension

1. Install "Remote - Containers" extension
2. Open project folder in VS Code
3. Click "Reopen in Container"
4. VS Code connects to running container

### Jupyter Extension

1. Install "Jupyter" extension in VS Code
2. Open a `.ipynb` file
3. Select kernel: "Python 3.11 (zipline-reloaded)"
4. Run cells

## Production Deployment

### Using Docker Swarm

```bash
docker swarm init
docker stack deploy -c docker-compose.yml zipline-stack
```

### Using Kubernetes

Convert to Kubernetes manifests:
```bash
kompose convert -f docker-compose.yml
kubectl apply -f .
```

### Security Considerations

For production:

1. **Enable authentication**:
   - Set strong Jupyter password
   - Use HTTPS/SSL

2. **Restrict access**:
   - Don't expose port 9000 publicly
   - Use VPN or SSH tunnel

3. **Resource limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
```

## Performance Tips

### Increase Performance

1. **Allocate more resources**:
   - Docker Desktop → Preferences → Resources
   - Increase CPU and Memory

2. **Use SSD for volumes**:
   - Store Docker volumes on SSD
   - Improves database query speed

3. **Optimize database queries**:
   - Use specific date ranges
   - Query only needed columns
   - Index databases properly

### Monitor Resource Usage

```bash
# Container stats
docker stats zipline-reloaded-jupyter

# Detailed info
docker exec zipline-reloaded-jupyter top
```

## Integration with Other Tools

### Connect to QuantConnect

```python
# In Jupyter notebook
from zipline.pipeline.data import create_custom_db, insert_custom_data
import pandas as pd

# Fetch data from QuantConnect API
# ... your code ...

# Store in zipline database
create_custom_db('qc-data', columns={...})
insert_custom_data('qc-data', data)
```

### Export to CSV

```python
from zipline.pipeline.data import query_custom_data

# Query data
data = query_custom_data('my-db')

# Export
data.to_csv('/data/export.csv')
```

### Import from CSV

```python
import pandas as pd
from zipline.pipeline.data import insert_custom_data

# Read CSV
data = pd.read_csv('/data/import.csv', index_col='date', parse_dates=True)

# Convert to MultiIndex format
# ... format conversion ...

# Insert
insert_custom_data('my-db', data)
```

## Cleaning Up

### Remove containers and volumes

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi zipline-reloaded:latest
```

### Clean Docker system

```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove all volumes
docker volume prune
```

## Getting Help

- **Documentation**: See `/docs` directory
- **Examples**: Check `/examples` directory
- **Notebooks**: Interactive tutorials in `/notebooks`
- **Issues**: https://github.com/stefan-jansen/zipline-reloaded/issues

## Summary

Quick command reference:

```bash
# Start
docker-compose up -d

# Access
http://localhost:9000

# Logs
docker-compose logs -f

# Shell
docker exec -it zipline-reloaded-jupyter bash

# Stop
docker-compose down

# Rebuild
docker-compose build
```

Happy trading! 🚀
