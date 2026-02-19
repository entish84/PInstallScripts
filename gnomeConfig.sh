#!/bin/bash

set -e
# This script is used to configure the Gnome desktop environment on a Linux system. It will set up the desktop, dock, and application folders.

# Create application folders with names A-E, F-J, K-O, P-T, U-Z and move the respective applications to those folders based on their names
echo "Creating application folders and organizing applications..."
# Use gsettings to create the folders and move the applications
gsettings set org.gnome.desktop.app-folders folder-children "['A-E', 'F-J', 'K-O', 'P-T', 'U-Z']"
# Get the list of applications in the applications folder and parse their gnome gsetting names from the .desktop files
applications=$(ls /usr/share/applications/*.desktop)
for app in $applications; do
    app_name=$(basename "$app" .desktop)
    first_letter=$(echo "$app_name" | cut -c 1 | tr '[:lower:]' '[:upper:]')
    if [[ "$first_letter" =~ [A-E] ]]; then
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-A-E/ name 'A-E'
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-A-E/ apps "$(gsettings get org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-A-E/ apps | sed "s/]/, '$(basename "$app" .desktop).desktop']/")"
    elif [[ "$first_letter" =~ [F-J] ]]; then
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-F-J/ name 'F-J'
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-F-J/ apps "$(gsettings get org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-F-J/ apps | sed "s/]/, '$(basename "$app" .desktop).desktop']/")"
    elif [[ "$first_letter" =~ [K-O] ]]; then
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-K-O/ name 'K-O'
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-K-O/ apps "$(gsettings get org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-K-O/ apps | sed "s/]/, '$(basename "$app" .desktop).desktop']/")"
    elif [[ "$first_letter" =~ [P-T] ]]; then
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-P-T/ name 'P-T'
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-P-T/ apps "$(gsettings get org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-P-T/ apps | sed "s/]/, '$(basename "$app" .desktop).desktop']/")"
    elif [[ "$first_letter" =~ [U-Z] ]]; then
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-U-Z/ name 'U-Z'
        gsettings set org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-U-Z/ apps "$(gsettings get org.gnome.desktop.app-folders folder:/org/gnome/desktop/app-folders/folder-U-Z/ apps | sed "s/]/, '$(basename "$app" .desktop).desktop']/")"
    fi
done
echo "Application folders created and applications organized!"

# Set up the dock with the following applications: Firefox, Kitty, Files, VsCode, Settings, FeatherPad
echo "Setting up the dock with the specified applications..."
gsettings set org.gnome.shell favorite-apps "['firefox.desktop', 'kitty.desktop', 'org.gnome.Nautilus.desktop', 'code.desktop', 'org.gnome.Settings.desktop', 'io.github.hartwork.image-viewer.desktop']"
echo "Dock set up with the specified applications!"

# Center new windows on the screen
echo "Centering new windows on the screen..."
gsettings set org.gnome.mutter center-new-windows true
echo "New windows will now be centered on the screen!"  

# Set the interface font as Inter Variable Regular 11 and the document font as Inter Variable Regular 11 and the monospace font as JetBrains Mono Nerd Regular 11
gsettings set org.gnome.desktop.interface font-name 'Inter Variable Regular 11'
gsettings set org.gnome.desktop.interface document-font-name 'Inter Variable Regular 11'
gsettings set org.gnome.desktop.interface monospace-font-name 'JetBrainsMono Nerd Regular 12'
echo "Interface, document, and monospace fonts set!"

# Reveal week numbers in the Gnome calendar
gsettings set org.gnome.desktop.calendar show-weekdate true

# Turn off ambient sensors for setting screen brightness (they rarely work well!)
gsettings set org.gnome.settings-daemon.plugins.power ambient-enabled false

# Using Catppuccin Mocha Color Pallete Set Gnome Background color and lock screen color.
# Set appropriate GTK, icon, and cursor themes to match the Catppuccin Mocha color palette.
gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'
gsettings set org.gnome.desktop.interface cursor-theme 'Yaru'
gsettings set org.gnome.desktop.interface gtk-theme "Yaru-blue-dark"
gsettings set org.gnome.desktop.interface icon-theme "Yaru-blue"
gsettings set org.gnome.desktop.interface accent-color "blue" 2>/dev/null || true
echo "Gnome desktop environment configured with Catppuccin Mocha color palette and matching themes!"

# Set the background and lock screen to Wall1.png from the wallpapers folder in the script directory
script_dir=$(dirname "$(realpath "$0")")
wallpaper_path="$script_dir/Walls/Wall1.png"
if [ -f "$wallpaper_path" ]; then
    gsettings set org.gnome.desktop.background picture-uri "file://$wallpaper_path"
    gsettings set org.gnome.desktop.screensaver picture-uri "file://$wallpaper_path"
    echo "Background and lock screen set to Wall1.png!"
else
    echo "Wall1.png not found in the wallpapers folder. Please make sure the file exists at $wallpaper_path."
fi

# SET KEYBINDINGS
gsettings set org.gnome.desktop.wm.keybindings close "['<Super>w']"

# Make it easy to maximize like you can fill left/right
gsettings set org.gnome.desktop.wm.keybindings maximize "['<Super>Up']"

# Make it easy to resize undecorated windows
gsettings set org.gnome.desktop.wm.keybindings begin-resize "['<Super>BackSpace']"

# For keyboards that only have a start/stop button for music, like Logitech MX Keys Mini
gsettings set org.gnome.settings-daemon.plugins.media-keys next "['<Shift>AudioPlay']"

# Full-screen with title/navigation bar
gsettings set org.gnome.desktop.wm.keybindings toggle-fullscreen "['<Shift>F11']"

# Use 6 fixed workspaces instead of dynamic mode
gsettings set org.gnome.mutter dynamic-workspaces false
gsettings set org.gnome.desktop.wm.preferences num-workspaces 6

# Disable the hotkeys in the Dash to Dock extension (most likely culprit)
gsettings set org.gnome.shell.extensions.dash-to-dock hot-keys false

# Use alt for pinned apps
gsettings set org.gnome.shell.keybindings switch-to-application-1 "['<Alt>1']"
gsettings set org.gnome.shell.keybindings switch-to-application-2 "['<Alt>2']"
gsettings set org.gnome.shell.keybindings switch-to-application-3 "['<Alt>3']"
gsettings set org.gnome.shell.keybindings switch-to-application-4 "['<Alt>4']"
gsettings set org.gnome.shell.keybindings switch-to-application-5 "['<Alt>5']"
gsettings set org.gnome.shell.keybindings switch-to-application-6 "['<Alt>6']"
gsettings set org.gnome.shell.keybindings switch-to-application-7 "['<Alt>7']"
gsettings set org.gnome.shell.keybindings switch-to-application-8 "['<Alt>8']"
gsettings set org.gnome.shell.keybindings switch-to-application-9 "['<Alt>9']"

# Use super for workspaces
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-1 "['<Super>1']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-2 "['<Super>2']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-3 "['<Super>3']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-4 "['<Super>4']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-5 "['<Super>5']"
gsettings set org.gnome.desktop.wm.keybindings switch-to-workspace-6 "['<Super>6']"
