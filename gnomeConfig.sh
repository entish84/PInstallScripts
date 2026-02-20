#!/bin/bash

# --- Robust GNOME Configuration Script ---

set -e

# Detect the real user
if [ "$EUID" -eq 0 ]; then
    if [ -n "$SUDO_USER" ]; then
        REAL_USER="$SUDO_USER"
        REAL_UID=$(id -u "$SUDO_USER")
    else
        echo "Error: This script is running as root but SUDO_USER is not set."
        echo "Please run this script as a normal user or via sudo from a user session."
        exit 1
    fi
else
    REAL_USER="$USER"
    REAL_UID=$(id -u)
fi

# Ensure D-Bus session bus address is set correctly for the real user
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$REAL_UID/bus"
fi

# Function to safely set gsettings
safe_gset() {
    local schema="$1"
    local key="$2"
    local value="$3"
    
    # Check if schema exists
    if gsettings list-schemas | grep -q "^$schema$"; then
        # Check if key exists in schema
        if gsettings list-keys "$schema" | grep -q "^$key$"; then
            echo "Setting $schema $key to $value"
            if [ "$EUID" -eq 0 ]; then
                sudo -u "$REAL_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" gsettings set "$schema" "$key" "$value"
            else
                gsettings set "$schema" "$key" "$value"
            fi
        else
            echo "Warning: Key '$key' not found in schema '$schema'. Skipping."
        fi
    else
        echo "Warning: Schema '$schema' not found. Skipping."
    fi
}

# Function to safely set relocatable schemas (like app-folders)
safe_gset_path() {
    local schema="$1"
    local path="$2"
    local key="$3"
    local value="$4"
    
    echo "Setting $schema at $path: $key to $value"
    if [ "$EUID" -eq 0 ]; then
        sudo -u "$REAL_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" gsettings set "$schema:$path" "$key" "$value" || echo "Warning: Failed to set $key at $path."
    else
        gsettings set "$schema:$path" "$key" "$value" || echo "Warning: Failed to set $key at $path."
    fi
}

echo "Starting GNOME configuration..."

# 1. Organize Applications into Folders
echo "Organizing applications into folders..."

# Initialize categories
declare -A folders=( ["A-E"]="" ["F-J"]="" ["K-O"]="" ["P-T"]="" ["U-Z"]="" )

# Collect installed applications
for app_path in /usr/share/applications/*.desktop; do
    [ -e "$app_path" ] || continue
    app_file=$(basename "$app_path")
    # Get first letter and convert to uppercase
    first_letter=$(echo "$app_file" | cut -c 1 | tr '[:lower:]' '[:upper:]')
    
    if [[ "$first_letter" =~ [A-E] ]]; then folders["A-E"]+="'$app_file', "
    elif [[ "$first_letter" =~ [F-J] ]]; then folders["F-J"]+="'$app_file', "
    elif [[ "$first_letter" =~ [K-O] ]]; then folders["K-O"]+="'$app_file', "
    elif [[ "$first_letter" =~ [P-T] ]]; then folders["P-T"]+="'$app_file', "
    elif [[ "$first_letter" =~ [U-Z] ]]; then folders["U-Z"]+="'$app_file', "
    fi
done

# Apply folder settings
folder_list="["
for folder in "${!folders[@]}"; do
    folder_list+="'$folder', "
    # Remove trailing comma and space
    apps="[${folders[$folder]%, }]"
    safe_gset_path "org.gnome.desktop.app-folders.folder" "/org/gnome/desktop/app-folders/folders/$folder/" "name" "'$folder'"
    safe_gset_path "org.gnome.desktop.app-folders.folder" "/org/gnome/desktop/app-folders/folders/$folder/" "apps" "$apps"
done
folder_list="${folder_list%, }]"

safe_gset "org.gnome.desktop.app-folders" "folder-children" "$folder_list"

# 2. Interface & Behavior
echo "Configuring interface and behavior..."
safe_gset "org.gnome.shell" "favorite-apps" "['firefox.desktop', 'kitty.desktop', 'org.gnome.Nautilus.desktop', 'code.desktop', 'org.gnome.Settings.desktop']"
safe_gset "org.gnome.mutter" "center-new-windows" "true"
safe_gset "org.gnome.desktop.calendar" "show-weekdate" "true"
safe_gset "org.gnome.settings-daemon.plugins.power" "ambient-enabled" "false"

# Fonts
safe_gset "org.gnome.desktop.interface" "font-name" "'Inter Variable Regular 11'"
safe_gset "org.gnome.desktop.interface" "document-font-name" "'Inter Variable Regular 11'"
safe_gset "org.gnome.desktop.interface" "monospace-font-name" "'JetBrainsMono Nerd Font Regular 11'"

# Theme & Appearance
safe_gset "org.gnome.desktop.interface" "color-scheme" "'prefer-dark'"
safe_gset "org.gnome.desktop.interface" "accent-color" "'blue'"
safe_gset "org.gnome.desktop.interface" "cursor-theme" "'Yaru'"
safe_gset "org.gnome.desktop.interface" "gtk-theme" "'Yaru-blue-dark'"
safe_gset "org.gnome.desktop.interface" "icon-theme" "'Yaru-blue'"

# Background
script_dir=$(dirname "$(realpath "$0")")
wallpaper_path="$script_dir/Walls/Wall1.png"
if [ -f "$wallpaper_path" ]; then
    safe_gset "org.gnome.desktop.background" "picture-uri" "'file://$wallpaper_path'"
    safe_gset "org.gnome.desktop.background" "picture-uri-dark" "'file://$wallpaper_path'"
    safe_gset "org.gnome.desktop.screensaver" "picture-uri" "'file://$wallpaper_path'"
fi

# 3. Keybindings & Workspaces
echo "Configuring workspaces and keybindings..."
safe_gset "org.gnome.mutter" "dynamic-workspaces" "false"
safe_gset "org.gnome.desktop.wm.preferences" "num-workspaces" "6"

# Window Management
safe_gset "org.gnome.desktop.wm.keybindings" "close" "['<Super>w']"
safe_gset "org.gnome.desktop.wm.keybindings" "maximize" "['<Super>Up']"
safe_gset "org.gnome.desktop.wm.keybindings" "begin-resize" "['<Super>BackSpace']"
safe_gset "org.gnome.desktop.wm.keybindings" "toggle-fullscreen" "['<Shift>F11']"

# Media Keys
safe_gset "org.gnome.settings-daemon.plugins.media-keys" "next" "['<Shift>AudioPlay']"

# Workspace Switching
for i in {1..6}; do
    safe_gset "org.gnome.desktop.wm.keybindings" "switch-to-workspace-$i" "['<Super>$i']"
    safe_gset "org.gnome.shell.keybindings" "switch-to-application-$i" "['<Alt>$i']"
done

# Dash to Dock (only if installed)
safe_gset "org.gnome.shell.extensions.dash-to-dock" "hot-keys" "false"

echo "GNOME configuration complete!"
