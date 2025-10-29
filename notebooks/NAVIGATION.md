# Jupyter Navigation Guide

Welcome to the Zipline Reloaded notebooks directory! You now have full access to the entire project structure directly from Jupyter.

## 📁 Available Directories

You can now access all these directories from the Jupyter file browser:

### 🏠 `project_root/`
**Full project root directory**
- Access everything in the project
- Navigate up to the parent directory
- View all top-level files (README.md, setup.py, etc.)

### 📜 `scripts/`
**Data management and utility scripts**
- `manage_data.py` - Bundle ingestion and data management
- `check_bundle_dates.py` - Check your data ranges
- `setup_extension.py` - Extension configuration

### 💻 `src/`
**Zipline source code**
- `zipline/` - Core Zipline library
- `zipline/data/bundles/` - Bundle implementations
- `zipline/pipeline/` - Pipeline factors

### 🧪 `tests/`
**Test suite**
- Unit tests
- Integration tests
- Test fixtures

### 📚 `docs/`
**Documentation**
- User guides
- API documentation
- Examples

### 📓 `strategies_files/`
**Your trading strategies (already available)**
- `sma_crossover.py`
- `ema_crossover.py`

## 🎯 How to Use

### In Jupyter File Browser:
1. Look at the left sidebar in Jupyter
2. You'll see folders: `project_root`, `scripts`, `src`, `strategies_files`, etc.
3. Click on any folder to explore it
4. Double-click files to open them

### Common Tasks:

#### Run Data Ingestion:
1. Click `scripts/` folder
2. Right-click `manage_data.py`
3. Open in editor to view
4. Or run in terminal: `python scripts/manage_data.py setup --source yahoo`

#### View Zipline Source Code:
1. Click `src/` folder
2. Navigate to `zipline/`
3. Explore the codebase

#### Check Bundle Data:
1. Click `scripts/` folder
2. Find `check_bundle_dates.py`
3. Or run: `%run check_data_range.py` in a notebook

#### Access Project Root Files:
1. Click `project_root/` folder
2. View README.md, setup.py, requirements.txt, etc.

## 🔗 Navigation Tips

**Going Up:**
- Click `project_root/` to see everything
- From there, you can navigate to any directory

**Direct Access:**
- Use symlinks for quick access to key folders
- No need to navigate through parent directories

**Terminal Commands:**
```bash
# All these work from the notebooks directory:
python scripts/manage_data.py setup --source yahoo
python scripts/check_bundle_dates.py
python ../setup.py --version
```

## 📝 File Access in Notebooks

You can now import or access files from anywhere:

```python
# Import from scripts
import sys
sys.path.insert(0, '../scripts')
from manage_data import ingest_bundle

# Read project files
with open('project_root/README.md') as f:
    readme = f.read()

# Access source code
with open('src/zipline/data/bundles/sharadar_bundle.py') as f:
    source = f.read()
```

## 🛠️ Editing Files

**Python Files:**
- Click on any `.py` file to open in Jupyter editor
- Edit and save
- Changes are immediately available

**Data Scripts:**
- Edit `scripts/manage_data.py` directly
- Modify ingestion logic
- Add new bundle types

**Strategies:**
- Edit `strategies_files/*.py`
- Create new strategies
- Test and iterate quickly

## ⚠️ Important Notes

1. **These are symbolic links** - changes you make will affect the actual files
2. **Be careful editing source code** - stick to scripts and strategies unless you know what you're doing
3. **Git tracking** - all changes are tracked in the repository

## 🎨 Customization

Want to add more directories? Run in a terminal:

```bash
cd /home/user/zipline-reloaded/notebooks
ln -s ../path/to/directory shortcut_name
```

## 🆘 Troubleshooting

**"Broken symlink" error:**
- The target directory was moved or deleted
- Re-create the symlink with the correct path

**"Permission denied":**
- Some directories may have restricted permissions
- Use a terminal with appropriate permissions

**Can't see changes:**
- Refresh the Jupyter file browser (F5)
- Or click the refresh icon in Jupyter

## 📚 Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Zipline Documentation](https://zipline.ml4trading.io)
- Project README: Click `project_root/README.md`
