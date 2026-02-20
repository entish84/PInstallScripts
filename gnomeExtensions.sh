#!/bin/bash

# --- Refactored GNOME Extensions Script for Arch Linux ---

set -e

# Detect the real user
if [ "$EUID" -eq 0 ]; then
    if [ -n "$SUDO_USER" ]; then
        REAL_USER="$SUDO_USER"
        REAL_UID=$(id -u "$SUDO_USER")
    else
        echo "Error: This script is running as root but SUDO_USER is not set."
        exit 1
    fi
else
    REAL_USER="$USER"
    REAL_UID=$(id -u)
fi

# Ensure D-Bus session bus address is set
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$REAL_UID/bus"
fi

# Function to run commands as the real user with D-Bus access
user_run() {
    if [ "$EUID" -eq 0 ]; then
        sudo -u "$REAL_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" "$@"
    else
        "$@"
    fi
}

echo "Installing Extension dependencies..."
sudo pacman -S --needed --noconfirm libgtop python-pipx

# Install gnome-extensions-cli if not present
if ! user_run pipx list | grep -q "gnome-extensions-cli"; then
    echo "Installing gnome-extensions-cli..."
    user_run pipx install gnome-extensions-cli --system-site-packages
fi

# Helper function for gext
gext() {
    user_run ~/.local/bin/gext "$@"
}

echo "Disabling default extensions..."
user_run gnome-extensions disable tiling-assistant@ubuntu.com || true
user_run gnome-extensions disable ubuntu-appindicators@ubuntu.com || true
user_run gnome-extensions disable ubuntu-dock@ubuntu.com || true
user_run gnome-extensions disable ding@rastersoft.com || true

# User prompt
echo -n "To install GNOME extensions, you need to accept some confirmations in the UI. Ready? (y/n): "
read -r response
if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Skipping extension installation."
    exit 0
fi

echo "Installing new extensions..."
extensions=(
    "tactile@lundal.io"
    "just-perfection-desktop@just-perfection"
    "blur-my-shell@aunetx"
    "space-bar@luchrioh"
    "undecorate@sun.wxg@gmail.com"
    "AlphabeticalAppGrid@stuarthayhurst"
)

for ext in "${extensions[@]}"; do
    echo "Installing $ext..."
    gext install "$ext" || echo "Warning: Failed to install $ext"
done

# --- Schema Installation ---
# gsettings needs the schemas to be in a known location and compiled.
# The most reliable way for CLI tools is to put them in the system path.
echo "Installing extension schemas system-wide..."
USER_EXT_DIR=$(user_run python3 -c "import os; print(os.path.expanduser('~/.local/share/gnome-shell/extensions'))")

for ext in "${extensions[@]}"; do
    SCHEMA_SRC="$USER_EXT_DIR/$ext/schemas"
    if [ -d "$SCHEMA_SRC" ]; then
        echo "Deploying schemas for $ext"
        sudo cp "$SCHEMA_SRC/"*.xml /usr/share/glib-2.0/schemas/ 2>/dev/null || true
    fi
done

echo "Compiling all system schemas..."
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

# Function to safely set gsettings as real user
safe_gset() {
    local schema="$1"
    local key="$2"
    local value="$3"
    echo "Setting $schema $key to $value"
    # Note: We don't use || true here so we can see if it still fails after schema sync
    user_run gsettings set "$schema" "$key" "$value" || echo "Warning: Could not set $key in $schema"
}

echo "Configuring extensions..."

# Tactile
safe_gset org.gnome.shell.extensions.tactile col-0 1
safe_gset org.gnome.shell.extensions.tactile col-1 1
safe_gset org.gnome.shell.extensions.tactile col-2 1
safe_gset org.gnome.shell.extensions.tactile col-3 1
safe_gset org.gnome.shell.extensions.tactile row-0 1
safe_gset org.gnome.shell.extensions.tactile row-1 1
safe_gset org.gnome.shell.extensions.tactile gap-size 16

# Just Perfection
safe_gset org.gnome.shell.extensions.just-perfection animation 2
safe_gset org.gnome.shell.extensions.just-perfection dash-app-running true
safe_gset org.gnome.shell.extensions.just-perfection workspace true
safe_gset org.gnome.shell.extensions.just-perfection workspace-popup false

# Blur My Shell (multiple schemas)
safe_gset org.gnome.shell.extensions.blur-my-shell.appfolder blur false
safe_gset org.gnome.shell.extensions.blur-my-shell.lockscreen blur false
safe_gset org.gnome.shell.extensions.blur-my-shell.screenshot blur false
safe_gset org.gnome.shell.extensions.blur-my-shell.window-list blur false
safe_gset org.gnome.shell.extensions.blur-my-shell.panel blur false
safe_gset org.gnome.shell.extensions.blur-my-shell.overview blur true
safe_gset org.gnome.shell.extensions.blur-my-shell.dash-to-dock blur true
safe_gset org.gnome.shell.extensions.blur-my-shell.dash-to-dock brightness 0.6
safe_gset org.gnome.shell.extensions.blur-my-shell.dash-to-dock sigma 30
safe_gset org.gnome.shell.extensions.blur-my-shell.dash-to-dock static-blur true

# Space Bar
safe_gset org.gnome.shell.extensions.space-bar.behavior smart-workspace-names false
safe_gset org.gnome.shell.extensions.space-bar.shortcuts enable-activate-workspace-shortcuts false
safe_gset org.gnome.shell.extensions.space-bar.shortcuts enable-move-to-workspace-shortcuts true

# AlphabeticalAppGrid (Corrected case)
safe_gset org.gnome.shell.extensions.AlphabeticalAppGrid folder-order-position "'end'"

echo "GNOME Extensions configuration complete! (You may need to restart GNOME Shell: Alt+F2, r, Enter)"
