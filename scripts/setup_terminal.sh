#!/bin/bash
# Setup Enhanced Terminal Configuration
# This script installs improved terminal settings for Jupyter

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Installing Enhanced Terminal Configuration                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Backup existing files if they exist
if [ -f ~/.bashrc ]; then
    echo "📦 Backing up existing ~/.bashrc to ~/.bashrc.backup"
    cp ~/.bashrc ~/.bashrc.backup
fi

if [ -f ~/.inputrc ]; then
    echo "📦 Backing up existing ~/.inputrc to ~/.inputrc.backup"
    cp ~/.inputrc ~/.inputrc.backup
fi

# Install .bashrc
echo "📝 Installing ~/.bashrc..."
cat > ~/.bashrc << 'BASHRC_EOF'
# ~/.bashrc - Enhanced Bash Configuration for Jupyter Terminal

# Command History Settings
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
shopt -s histappend
shopt -s cmdhist
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

# Keyboard Shortcuts
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'
bind '"\C-r": reverse-search-history'
bind '"\e.": yank-last-arg'

# Auto-completion
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi
bind "set completion-ignore-case on"
bind "set show-all-if-ambiguous on"
bind "set mark-symlinked-directories on"

# Colorful Prompt
RED='\[\033[0;31m\]'
GREEN='\[\033[0;32m\]'
YELLOW='\[\033[0;33m\]'
BLUE='\[\033[0;34m\]'
RESET='\[\033[0m\]'

parse_git_branch() {
    git branch 2> /dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

export PS1="${GREEN}\u@zipline${RESET}:${BLUE}\w${YELLOW}\$(parse_git_branch)${RESET}\$ "

# Navigation Aliases
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias ~='cd ~'
alias -- -='cd -'

# List Files
alias ll='ls -lah'
alias la='ls -A'
alias l='ls -CF'
alias lt='ls -lhtrA'
alias ls='ls --color=auto'

# Safety
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Colorize
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'

# Git Shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --decorate'
alias gd='git diff'

# Zipline Shortcuts
alias zp='cd /home/user/zipline-reloaded'
alias zn='cd /home/user/zipline-reloaded/notebooks'
alias zs='cd /home/user/zipline-reloaded/scripts'
alias python='python3'
alias pip='pip3'
alias ingest-yahoo='python /home/user/zipline-reloaded/scripts/manage_data.py setup --source yahoo'
alias check-bundles='python /home/user/zipline-reloaded/scripts/check_bundle_dates.py'

# Useful Functions
h() {
    if [ -z "$1" ]; then
        history 20
    else
        history | grep "$1"
    fi
}

mkcd() {
    mkdir -p "$1" && cd "$1"
}

extract() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"     ;;
            *.tar.gz)    tar xzf "$1"     ;;
            *.bz2)       bunzip2 "$1"     ;;
            *.gz)        gunzip "$1"      ;;
            *.tar)       tar xf "$1"      ;;
            *.zip)       unzip "$1"       ;;
            *)           echo "'$1' cannot be extracted" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

top-commands() {
    history | awk '{print $2}' | sort | uniq -c | sort -rn | head -10
}

# Welcome Message
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        Zipline Reloaded - Enhanced Terminal                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Quick tips:"
echo "  ↑/↓     - Search history (type first, then use arrows!)"
echo "  Ctrl+R  - Reverse search history"
echo "  Tab     - Auto-complete"
echo "  zp/zn/zs - Jump to project/notebooks/scripts"
echo "  h <word> - Search command history"
echo ""
echo "See notebooks/TERMINAL_GUIDE.md for complete guide!"
echo ""
BASHRC_EOF

# Install .inputrc
echo "📝 Installing ~/.inputrc..."
cat > ~/.inputrc << 'INPUTRC_EOF'
# ~/.inputrc - Enhanced readline configuration

# Completion Settings
set completion-ignore-case on
set completion-map-case on
set show-all-if-ambiguous on
set show-all-if-unmodified on
set mark-directories on
set mark-symlinked-directories on
set colored-stats on
set visible-stats on
set colored-completion-prefix on

# Enable features
set input-meta on
set output-meta on
set convert-meta off
set enable-bracketed-paste on

# Keybindings
"\e[A": history-search-backward
"\e[B": history-search-forward
"\e[1;3D": backward-word
"\e[1;3C": forward-word
"\e[1;5D": backward-word
"\e[1;5C": forward-word
"\e[H": beginning-of-line
"\e[F": end-of-line
"\e[3~": delete-char
"\e[5~": history-search-backward
"\e[6~": history-search-forward
"\e\d": backward-kill-word
"\C-h": backward-kill-word

# No beeping
set bell-style none

# Display Settings
set completion-display-width 0
set completion-query-items 200
set page-completions on
set skip-completed-text on
set meta-flag on
INPUTRC_EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "To activate the changes:"
echo "  1. Open a NEW Jupyter terminal, or"
echo "  2. Run: source ~/.bashrc"
echo ""
echo "See notebooks/TERMINAL_GUIDE.md for all features and shortcuts!"
echo ""
