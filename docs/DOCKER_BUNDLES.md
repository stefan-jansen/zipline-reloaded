# Using Zipline Bundles in Docker

This guide shows you how to use the zipline bundle system inside the Docker environment for persistent, production-ready backtesting.

## Quick Start

```bash
# 1. Create .env file with your API keys (optional, for NASDAQ)
cp .env.example .env
# Edit .env and add: NASDAQ_DATA_LINK_API_KEY=your_key_here

# 2. Start the container
docker compose up -d

# 3. Setup a bundle (from inside container)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# 4. Access Jupyter at http://localhost:9000
# Open notebooks/05_backtesting_with_bundles.ipynb
```

## Bundle Storage in Docker

### Where Bundles Are Stored

Bundles are stored in a **Docker volume** which persists between container restarts:

```
Docker Volume: zipline-data
Container Path: /root/.zipline/
Contains: All bundle data in bcolz format
```

**Important**: This volume is persistent! Your data survives:
- Container restarts
- Container rebuilds
- Docker Compose down/up cycles

### Volume Management

```bash
# List Docker volumes
docker volume ls | grep zipline

# Inspect the bundle volume
docker volume inspect zipline-reloaded_zipline-data

# Backup the bundle data
docker run --rm -v zipline-reloaded_zipline-data:/data -v $(pwd):/backup ubuntu tar czf /backup/zipline-bundles-backup.tar.gz /data

# Restore from backup
docker run --rm -v zipline-reloaded_zipline-data:/data -v $(pwd):/backup ubuntu tar xzf /backup/zipline-bundles-backup.tar.gz -C /
```

## Setting Up Bundles

### Method 1: From Host Machine

```bash
# Setup Yahoo Finance bundle (free, no API key needed)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# Setup with custom tickers
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL,AMZN,TSLA

# Setup NASDAQ bundle (requires API key in .env)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset EOD
```

### Method 2: From Inside Container

```bash
# Enter container shell
docker exec -it zipline-reloaded-jupyter bash

# Inside container:
python /scripts/manage_data.py setup --source yahoo
python /scripts/manage_data.py list
exit
```

### Method 3: From Jupyter Notebook

```python
# In a Jupyter notebook cell:
!python /scripts/manage_data.py setup --source yahoo --tickers AAPL,MSFT,GOOGL
```

## Daily Updates

### Manual Update

```bash
# Update specific bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --bundle yahoo

# Update all bundles
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py update --all
```

### Automated Updates (Recommended)

**Option A: Host Cron (Recommended)**

The container must be running. Add to your host's crontab:

```bash
# Edit crontab on host
crontab -e

# Add this line (runs at 5 PM ET, Monday-Friday)
0 17 * * 1-5 docker exec zipline-reloaded-jupyter python /scripts/manage_data.py update --all >> /var/log/zipline_update.log 2>&1
```

**Option B: Separate Update Container**

Create `docker compose.override.yml`:

```yaml
version: '3.8'

services:
  zipline-updater:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: zipline-updater
    volumes:
      - zipline-data:/root/.zipline
      - ./scripts:/scripts
    environment:
      - NASDAQ_DATA_LINK_API_KEY=${NASDAQ_DATA_LINK_API_KEY:-}
    command: python /scripts/manage_data.py update --all
    restart: "no"
```

Then schedule on host:
```bash
# Runs updater container at 5 PM ET
0 17 * * 1-5 cd /path/to/zipline-reloaded && docker compose run --rm zipline-updater
```

**Option C: Inside Container with Cron**

```bash
# Enter container
docker exec -it zipline-reloaded-jupyter bash

# Install cron (if not already installed)
apt-get update && apt-get install -y cron

# Add cron job
echo "0 17 * * 1-5 python /scripts/manage_data.py update --all >> /var/log/zipline_update.log 2>&1" | crontab -

# Start cron
service cron start
```

## Using Bundles in Backtests

### From Jupyter Notebook

```python
import pandas as pd
from zipline import run_algorithm
from zipline.api import order_target_percent, symbol

def initialize(context):
    context.stock = symbol('AAPL')

def handle_data(context, data):
    order_target_percent(context.stock, 1.0)

# Run backtest using bundle
results = run_algorithm(
    start=pd.Timestamp('2022-01-01', tz='UTC'),
    end=pd.Timestamp('2023-12-31', tz='UTC'),
    initialize=initialize,
    handle_data=handle_data,
    capital_base=100000,
    bundle='yahoo',  # Bundle is persistent in Docker volume!
)

print(f"Total Return: {(results['portfolio_value'].iloc[-1] / 100000 - 1) * 100:.2f}%")
```

### From Python Script

Create `my_strategy.py` in notebooks directory:

```python
#!/usr/bin/env python
import pandas as pd
from zipline import run_algorithm
# ... your strategy ...

if __name__ == '__main__':
    results = run_algorithm(..., bundle='yahoo')
    print(results['portfolio_value'].tail())
```

Run it:
```bash
docker exec -it zipline-reloaded-jupyter python /notebooks/my_strategy.py
```

## API Keys Setup

### For NASDAQ Data Link

**Option 1: .env File (Recommended)**

```bash
# On host machine, edit .env file
echo "NASDAQ_DATA_LINK_API_KEY=your_actual_key_here" >> .env

# Restart container to load new environment
docker compose restart
```

**Option 2: Set in docker-compose.yml**

Edit `docker-compose.yml`:
```yaml
environment:
  - NASDAQ_DATA_LINK_API_KEY=your_key_here  # Not recommended for git repos
```

**Option 3: Pass at Runtime**

```bash
docker exec -it -e NASDAQ_DATA_LINK_API_KEY=your_key zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq
```

## Bundle Management

### Check Available Bundles

```bash
# From host
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py list

# Or using zipline directly
docker exec -it zipline-reloaded-jupyter zipline bundles
```

### Clean Old Data

```bash
# Keep last 3 ingestions
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py clean --bundle yahoo --keep-last 3

# Using zipline directly
docker exec -it zipline-reloaded-jupyter zipline clean -b yahoo --keep-last 3
```

### Check Bundle Storage Size

```bash
# From inside container
docker exec -it zipline-reloaded-jupyter du -sh /root/.zipline/data/*

# Check volume size from host
docker system df -v | grep zipline
```

## Troubleshooting

### Bundle Not Found

**Problem**: `Error: No bundle registered with name 'yahoo'`

**Solution**:
```bash
# Check what's available
docker exec -it zipline-reloaded-jupyter zipline bundles

# Re-register and ingest
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo
```

### API Key Not Working

**Problem**: `NASDAQ_DATA_LINK_API_KEY environment variable not set`

**Solution**:
```bash
# Verify environment variable
docker exec -it zipline-reloaded-jupyter env | grep NASDAQ

# If not set, add to .env and restart
echo "NASDAQ_DATA_LINK_API_KEY=your_key" >> .env
docker compose restart

# Verify again
docker exec -it zipline-reloaded-jupyter env | grep NASDAQ
```

### Out of Space

**Problem**: Docker volume is full

**Solution**:
```bash
# Check size
docker system df -v

# Clean old ingestions
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py clean --bundle yahoo --keep-last 2

# Or prune all unused Docker resources
docker system prune -a --volumes
```

### Container Restart Loses Data

**Problem**: Bundles disappear after restart

**Check**:
```bash
# Verify volume is mounted
docker inspect zipline-reloaded-jupyter | grep Mounts -A 20

# Should see: "Destination": "/root/.zipline"
```

If not mounted, check `docker-compose.yml` has:
```yaml
volumes:
  - zipline-data:/root/.zipline
```

### Permission Issues

**Problem**: Permission denied errors

**Solution**:
```bash
# Fix permissions inside container
docker exec -it zipline-reloaded-jupyter chown -R root:root /root/.zipline
docker exec -it zipline-reloaded-jupyter chmod -R 755 /root/.zipline
```

## Performance Tips

### 1. Use SSD for Docker Volumes

Docker volumes perform best on SSD storage. Configure Docker to use SSD:

**Linux**:
```bash
# Edit /etc/docker/daemon.json
{
  "data-root": "/path/to/ssd/docker"
}

# Restart Docker
sudo systemctl restart docker
```

**Mac/Windows**: Docker Desktop → Settings → Resources → Advanced → Disk image location

### 2. Allocate Enough Resources

**Docker Desktop Settings**:
- Memory: At least 4GB (8GB recommended)
- CPUs: 2+ cores
- Swap: 2GB
- Disk: 20GB+ for bundles

### 3. Use `.dockerignore`

Ensure `.dockerignore` excludes large files:
```
data/
notebooks/.ipynb_checkpoints/
**/__pycache__/
*.pyc
.git/
```

## Production Deployment

### Docker Compose Production Setup

`docker compose.prod.yml`:
```yaml
version: '3.8'

services:
  zipline-jupyter:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    volumes:
      - ./notebooks:/notebooks
      - ./data:/data
      - zipline-data:/root/.zipline
      - ./scripts:/scripts
    environment:
      - ZIPLINE_ROOT=/root/.zipline
      - NASDAQ_DATA_LINK_API_KEY=${NASDAQ_DATA_LINK_API_KEY}
    ports:
      - "127.0.0.1:8888:8888"  # Bind to localhost only
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  zipline-data:
    driver: local
```

### Start in Production

```bash
docker compose -f docker compose.prod.yml up -d
```

### Monitor Logs

```bash
# Follow logs
docker compose logs -f

# Check recent errors
docker compose logs --tail=50 | grep ERROR
```

## Best Practices

1. **Always use volumes for bundle data** - Never store in container filesystem
2. **Regular backups** - Backup the `zipline-data` volume weekly
3. **Monitor disk space** - Set up alerts for Docker volume usage
4. **Automate updates** - Use host cron for reliability
5. **Test before production** - Always test strategies with small capital first
6. **Keep multiple ingestions** - Use `--keep-last 3` when cleaning
7. **Use .env for secrets** - Never commit API keys to git
8. **Check logs** - Review update logs regularly

## Example: Complete Docker Workflow

```bash
# 1. Initial setup
git clone https://github.com/stefan-jansen/zipline-reloaded.git
cd zipline-reloaded
cp .env.example .env
# Edit .env with your API keys

# 2. Start Docker
docker compose up -d

# 3. Setup Yahoo bundle
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source yahoo

# 4. Setup NASDAQ bundle (if you have API key)
docker exec -it zipline-reloaded-jupyter python /scripts/manage_data.py setup --source nasdaq --dataset EOD

# 5. Verify bundles
docker exec -it zipline-reloaded-jupyter zipline bundles

# 6. Setup automated updates (on host)
(crontab -l 2>/dev/null; echo "0 17 * * 1-5 docker exec zipline-reloaded-jupyter python /scripts/manage_data.py update --all") | crontab -

# 7. Open Jupyter
open http://localhost:9000

# 8. Run backtest in notebook
# Use notebooks/05_backtesting_with_bundles.ipynb
```

## Summary

✅ **Persistent Storage**: Bundles stored in Docker volume, survive restarts
✅ **Easy Setup**: One command to setup any bundle
✅ **Automated Updates**: Cron integration for daily data refresh
✅ **API Support**: Full support for API keys via .env
✅ **Production Ready**: Suitable for live deployment

Your bundle data is safe, persistent, and ready for professional backtesting! 🚀
