#!/bin/bash
# Test if enhanced terminal is working

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              Terminal Configuration Test                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Check if .bashrc exists
echo "Test 1: Checking for ~/.bashrc..."
if [ -f ~/.bashrc ]; then
    echo "  ✅ ~/.bashrc exists"
else
    echo "  ❌ ~/.bashrc missing - run: bash scripts/setup_terminal.sh"
    exit 1
fi

# Test 2: Check if .inputrc exists
echo "Test 2: Checking for ~/.inputrc..."
if [ -f ~/.inputrc ]; then
    echo "  ✅ ~/.inputrc exists"
else
    echo "  ❌ ~/.inputrc missing - run: bash scripts/setup_terminal.sh"
    exit 1
fi

# Test 3: Check if aliases are loaded
echo "Test 3: Checking if aliases are loaded..."
if alias zp &>/dev/null; then
    echo "  ✅ Aliases loaded (zp, zn, zs work)"
else
    echo "  ❌ Aliases not loaded - run: source ~/.bashrc"
fi

# Test 4: Check if functions are loaded
echo "Test 4: Checking if functions are loaded..."
if declare -f h &>/dev/null; then
    echo "  ✅ Functions loaded (h command works)"
else
    echo "  ❌ Functions not loaded - run: source ~/.bashrc"
fi

# Test 5: Check PS1 prompt
echo "Test 5: Checking prompt configuration..."
if [[ $PS1 == *"zipline"* ]]; then
    echo "  ✅ Custom prompt configured"
else
    echo "  ⚠️  Default prompt (still works, but not colorful)"
fi

# Test 6: Check history settings
echo "Test 6: Checking history settings..."
if [[ $HISTSIZE == "10000" ]]; then
    echo "  ✅ Extended history enabled (10,000 commands)"
else
    echo "  ⚠️  Default history size (only 500 commands)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                  Test Complete                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if this is an interactive shell
if [[ $- == *i* ]]; then
    echo "Shell is interactive ✅"
    echo ""
    echo "Try these commands to test:"
    echo "  1. Type 'zs' to jump to scripts directory"
    echo "  2. Type 'h' to see recent commands"
    echo "  3. Press Ctrl+R and type 'python' to search history"
    echo "  4. Type 'python scr' and press Tab to auto-complete"
else
    echo "Shell is NOT interactive ⚠️"
    echo "This is normal when running this script."
    echo "Open a new Jupyter Terminal to test interactively."
fi

echo ""
