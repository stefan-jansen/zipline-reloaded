# Enhanced Terminal Guide

Your Jupyter terminal has been configured with powerful features to make your workflow much faster and more efficient!

## 🎯 Quick Start

**Open a new Jupyter Terminal:**
1. In Jupyter, click **New** → **Terminal**
2. You'll see a colorful welcome message with tips
3. Start using the enhanced features immediately!

## ⌨️ Essential Keyboard Shortcuts

### Navigation
- `↑` / `↓` - **Type part of a command, then use arrows to search history**
  - Example: Type `python`, then ↑ to see all previous `python` commands
- `Ctrl+R` - **Reverse search** - type to search all history
  - Press `Ctrl+R`, type `ingest`, see all ingestion commands
- `Ctrl+A` - Jump to **beginning** of line
- `Ctrl+E` - Jump to **end** of line
- `Alt+←` / `Alt+→` - Move by **words**
- `Home` / `End` - Jump to start/end of line

### Editing
- `Ctrl+W` - Delete word **backward**
- `Ctrl+U` - Delete from cursor to **start** of line
- `Ctrl+K` - Delete from cursor to **end** of line
- `Alt+Backspace` - Delete word backward
- `Alt+.` - Insert **last argument** from previous command
  - Super useful! Type `cd `, then `Alt+.` to insert last file/directory

### History
- `Ctrl+R` - **Search history** (press again to cycle through matches)
- `Ctrl+G` - Exit history search
- `h keyword` - Search history for keyword (custom function)
- `history` - Show recent commands

### Completion
- `Tab` - **Auto-complete** files, directories, commands
  - Case-insensitive!
  - Shows all options immediately
  - Works with partial matches

### Screen Control
- `Ctrl+L` - **Clear screen** (keeps command you're typing)
- `Ctrl+C` - Cancel current command
- `Ctrl+D` - Exit terminal (or EOF)

## 🚀 Quick Navigation Aliases

Jump to important directories instantly:

```bash
zp          # Go to project root (/home/user/zipline-reloaded)
zn          # Go to notebooks
zs          # Go to scripts

..          # Go up one directory
...         # Go up two directories
....        # Go up three directories
-           # Go to previous directory
~           # Go home
```

**Examples:**
```bash
zs                    # Jump to scripts directory
cd ..                 # Go up one level
-                     # Go back to scripts
```

## 📂 File Listing Aliases

```bash
ll          # List all files with details (long format)
la          # List all files including hidden
lt          # List files sorted by date (newest last)
l           # List in columns

# Examples:
ll *.py     # List all Python files with details
lt          # See what you edited most recently
```

## 🔧 Git Shortcuts

```bash
gs          # git status
ga          # git add
ga .        # git add everything
gc          # git commit
gc -m "msg" # git commit with message
gp          # git push
gl          # git log (pretty format with graph)
gd          # git diff
```

## 🐍 Python & Zipline Aliases

```bash
python      # Always uses python3
pip         # Always uses pip3

# Zipline commands
ingest-yahoo      # Quick: python scripts/manage_data.py setup --source yahoo
check-bundles     # Quick: python scripts/check_bundle_dates.py
```

**Examples:**
```bash
ingest-yahoo                                    # Ingest Yahoo data (easy!)
check-bundles                                   # Check what data you have
python scripts/manage_data.py setup --source sharadar --tickers AAPL,MSFT
```

## 🛠️ Useful Functions

### Search History
```bash
h               # Show last 20 commands
h python        # Search history for "python"
h ingest        # Search history for "ingest"
top-commands    # Show your 10 most-used commands
```

### Make and Change Directory
```bash
mkcd myproject  # Create directory and cd into it
```

### Extract Archives
```bash
extract file.tar.gz   # Automatically extracts any archive type
extract bundle.zip    # Works with .zip, .tar, .gz, .bz2, etc.
```

## 🎨 Colorful Prompt

Your prompt shows:
- **Username** and **hostname** (in green)
- **Current directory** (in blue)
- **Git branch** (in yellow, if in a git repo)

Example:
```
user@zipline:~/zipline-reloaded/notebooks (main)$
```

## 💡 Pro Tips

### 1. Start Typing, Then Use Arrows
Instead of scrolling through all history, type what you remember:
```bash
python scri    # Type this
↑              # Then press up arrow
# Shows only commands starting with "python scri"
```

### 2. Use Ctrl+R for Fuzzy Search
```bash
Ctrl+R         # Press this
# Type: "ingest"
# See: python scripts/manage_data.py setup --source sharadar
# Press Ctrl+R again to see next match
# Press Enter to run it
```

### 3. Reuse Last Argument
```bash
ls /long/path/to/directory
cd Alt+.       # Inserts "/long/path/to/directory"
```

### 4. Quick Edits
Made a typo at the beginning?
```bash
pyton scripts/manage_data.py    # Oops, "pyton"
Ctrl+A                           # Jump to start
→→→→→                           # Move to the typo
# Fix it
```

### 5. Tab Completion Everywhere
```bash
python scr<Tab>               # Completes to "scripts/"
python scripts/man<Tab>       # Completes to "manage_data.py"
cd /home/user/zip<Tab>        # Completes to "zipline-reloaded/"
```

## 📋 Common Workflows

### Data Ingestion
```bash
zs                                              # Go to scripts
python manage_data.py setup --source yahoo     # Ingest data
check-bundles                                   # Verify it worked
```

### Git Workflow
```bash
zp              # Go to project root
gs              # Check status
ga .            # Add all changes
gc -m "feat: add new strategy"
gp              # Push
```

### Running Notebooks
```bash
zn                      # Go to notebooks
ls *.ipynb              # See available notebooks
jupyter notebook        # Start Jupyter (if not already running)
```

### Checking Data
```bash
check-bundles                    # See all bundles
python scripts/check_bundle_dates.py sharadar    # Check specific bundle
```

## 🔍 History Search Examples

### Find That Command You Ran Yesterday
```bash
h ingest           # Find all ingestion commands
h "setup --source" # Find setup commands
history | grep python  # Search for python commands
```

### Run Previous Command Again
```bash
↑              # Previous command
↑↑             # Two commands ago
!!             # Repeat last command
!$             # Use last argument from previous command
```

## ⚙️ Customization

### Add Your Own Aliases
Edit `~/.bashrc`:
```bash
nano ~/.bashrc

# Add at the bottom:
alias mycommand='python /path/to/script.py'

# Save and reload:
source ~/.bashrc
```

### Change Colors
Edit the `PS1` variable in `~/.bashrc` to customize your prompt colors.

### Disable Welcome Message
Comment out the echo commands at the end of `~/.bashrc`.

## 🆘 Troubleshooting

### Keyboard Shortcuts Not Working?
- Make sure you opened a **new** terminal after setup
- Or run: `source ~/.bashrc` in your current terminal

### Tab Completion Not Working?
Check if bash-completion is installed:
```bash
ls /etc/bash_completion
```

### Want to Reset?
```bash
rm ~/.bashrc ~/.inputrc
# Open new terminal to get defaults back
```

## 📚 Learn More

### Common Terminal Shortcuts Reference
- [Bash Shortcuts Cheatsheet](https://github.com/fliptheweb/bash-shortcuts-cheat-sheet)
- [GNU Readline Documentation](https://tiswww.case.edu/php/chet/readline/rluserman.html)

### Advanced Usage
- Use `man bash` to see all Bash features
- Use `man readline` to see all line editing features

---

**Enjoy your enhanced terminal!** 🚀

Type `h` to see recent commands, or start typing and use ↑/↓ to search history!
