#!/usr/bin/env python3

import os
import subprocess
from colorama import Fore, Style, init

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"{Fore.GREEN}{result.stdout}{Style.RESET_ALL}")
        write_log(f"Command output : {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error running command: {e.stderr}{Style.RESET_ALL}")
        write_log(f"Command error: {e.stderr}")
        return e


def get_user_input(prompt):
    # Clean the input to avoid issues with special characters
    user_input = input(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}")
    write_log(f"User input: {user_input}")
    return user_input.strip()

def write_log(message):
    with open(logfile, "a") as log_file:
        log_file.write(f"{message}\n")

#############################

logFolder = "logs"
if not os.path.exists(logFolder):
    os.makedirs(logFolder, exist_ok=True)
logfile = f"{logFolder}/arch-pi-script.log"
# If the log file exists, rename with timestamp to avoid overwriting previous logs, otherwise create a new log file
if os.path.exists(logfile):
    timestamp = subprocess.run(["date", "+%Y%m%d-%H%M%S"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    os.rename(logfile, f"{logfile}_{timestamp}")        
open(logfile, "w").close()
init(autoreset=True)

#############################

# Update and upgrade the system
run_command(["sudo", "pacman", "-Syu", "--noconfirm"])
run_command(["sudo", "yay", "-Syu", "--noconfirm"])

# Get the current username for later use in SSH key generation from the current environment
current_username = os.environ.get("USER", "default_user")
write_log(f"Current username: {current_username}")

#############################

# Install essential development tools
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing essential development tools...{Style.RESET_ALL}")
commandList = [
    "base-devel","git","gcc","make","clang","cargo","just","curl","wget","unzip","unrar","p7zip","xclip","wl-clipboard"
]

for cmd in commandList:
    print(f"{Fore.CYAN}Installing {cmd}...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", cmd, "--noconfirm", "--needed"])
    write_log(f"Installed {cmd} successfully.")
    print(f"{Fore.CYAN}Successfully installed {cmd}!{Style.RESET_ALL}")

#############################

# Accept GIT user name and email
print(f"{Style.BRIGHT}{Fore.YELLOW}Configuring GIT user settings...{Style.RESET_ALL}")
ISTEST=True
if ISTEST:
    git_user_name = "entish84"
    git_user_email = "entishthoughts@outlook.com"
else:
    git_user_name = get_user_input("Enter your GIT user name: ")
    git_user_email = get_user_input("Enter your GIT user email: ")

# Configure GIT with the provided user name and email
run_command(["git", "config", "--global", "user.name", git_user_name])
run_command(["git", "config", "--global", "user.email", git_user_email])
print(f"{Fore.CYAN}Successfully configured GIT with user name '{git_user_name}' and email '{git_user_email}'!{Style.RESET_ALL}")
write_log(f"Configured GIT with user name '{git_user_name}' and email '{git_user_email}' successfully.")

#############################

# Check if ssh is installed, and if not, install it
print(f"{Style.BRIGHT}{Fore.YELLOW}Checking for SSH installation...{Style.RESET_ALL}")
ssh_check = subprocess.run(["which", "ssh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if ssh_check.returncode != 0:
    print(f"{Fore.YELLOW}SSH is not installed. Installing SSH...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", "openssh", "--noconfirm", "--needed"])
    print(f"{Fore.CYAN}Successfully installed SSH!{Style.RESET_ALL}")
    write_log("Successfully installed SSH.")
else:
    print(f"{Fore.GREEN}SSH is already installed at {ssh_check.stdout.strip()}!{Style.RESET_ALL}")
write_log(f"Checked for SSH installation successfully. SSH is installed at {ssh_check.stdout.strip()}.")

#############################

# Generate SSH keys ed25519 for GIT and add them to the ssh-agent
print(f"{Style.BRIGHT}{Fore.YELLOW}Generating SSH keys for GIT...{Style.RESET_ALL}")
# Take GIT email as the comment for the SSH key, and save the key in the user's home directory under .ssh/id_ed25519
ssh_key_dir = f"/home/{current_username}/.ssh"
if not os.path.exists(ssh_key_dir):
    os.makedirs(ssh_key_dir, exist_ok=True)
write_log(f"Ensured SSH key directory exists at {ssh_key_dir}.")
# Prepare the Path
ssh_key_path = f"{ssh_key_dir}/id_ed25519"
write_log(f"SSH key path set to {ssh_key_path}.")
# Check if the SSH key already exists, and if so, skip generation
if os.path.exists(ssh_key_path):
    print(f"{Fore.YELLOW}SSH key already exists at {ssh_key_path}, skipping generation.{Style.RESET_ALL}")
    write_log(f"SSH key already exists at {ssh_key_path}, skipping generation.")
else:
    run_command(["ssh-keygen", "-t", "ed25519", "-C", git_user_email, "-f", ssh_key_path, "-N", ""])
    # Start the ssh-agent and add the generated SSH key to it    
    run_command(["echo", "$SSH_AGENT_PID", "&&", "ssh-add", ssh_key_path])
    print(f"{Fore.CYAN}Successfully generated SSH keys and added them to the ssh-agent!{Style.RESET_ALL}")
    write_log(f"Successfully generated SSH keys and added them to the ssh-agent.")

# Display the public key for the user to add to their GIT hosting service
with open(f"{ssh_key_path}.pub", "r") as pubkey_file:
    public_key = pubkey_file.read()
    os.environ["GITPUBKEY"] = public_key.strip()
print(f"{Fore.GREEN}Your SSH public key for GIT is available in the environment variable GITPUBKEY.{Style.RESET_ALL}")
print(f"{Fore.YELLOW}Add this SSH public key to your GIT hosting service to enable SSH authentication.{Style.RESET_ALL}")
write_log(f"Displaying SSH public key for GIT: {public_key}")

#############################

# Install Inter font, JetBrains Mono Nerd font, Fira Code Nerd font.
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing fonts...{Style.RESET_ALL}")
font_command_list = [
    "inter-font","ttf-jetbrains-mono-nerd","ttf-firacode-nerd"
]
for font_cmd in font_command_list:
    print(f"{Fore.CYAN}Installing {font_cmd}...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", font_cmd, "--noconfirm", "--needed"])
    print(f"{Fore.CYAN}Successfully installed {font_cmd}!{Style.RESET_ALL}")
write_log(f"Successfully installed fonts: {', '.join(font_command_list)}.")

#############################

# Install Zsh and Oh My Zsh and set Zsh as the default shell
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Zsh and Oh My Zsh...{Style.RESET_ALL}")
# If zsh is already present, skip installation, otherwise install zsh using pacman. Check using default shell path for zsh which is usually /bin/zsh or /usr/bin/zsh
zsh_path = ["/bin/zsh", "/usr/bin/zsh"]
zsh_installed = False
for path in zsh_path:
    if os.path.exists(path):
        zsh_installed = True
        print(f"{Fore.GREEN}Zsh is already installed at {path}, skipping installation.{Style.RESET_ALL}")
        write_log(f"Zsh is already installed at {path}, skipping installation.")
        break
if not zsh_installed:
    run_command(["sudo", "pacman", "-S", "zsh", "--noconfirm", "--needed"])
    write_log(f"Successfully installed Zsh.")

# Check if Oh My Zsh is already installed by checking the existence of the .oh-my-zsh directory in the user's home directory, and if not, install it using the official installation script from the Oh My Zsh GitHub repository
ohmyzsh_dir = f"/home/{current_username}/.oh-my-zsh"
if os.path.exists(ohmyzsh_dir):
    print(f"{Fore.YELLOW}Oh My Zsh is already installed at {ohmyzsh_dir}, skipping installation.{Style.RESET_ALL}")
    write_log(f"Oh My Zsh is already installed at {ohmyzsh_dir}, skipping installation.")
else:
    # Install Oh My Zsh using the official installation script from the Oh My Zsh GitHub repository, and run it in a non-interactive mode
    run_command(["bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh) --unattended"])
    print(f"{Fore.CYAN}Successfully installed Oh My Zsh!{Style.RESET_ALL}")
    write_log(f"Successfully installed Oh My Zsh.")

# Change the default shell to Zsh for the current user
run_command(["sudo", "chsh", "-s", "/bin/zsh", current_username])
print(f"{Fore.CYAN}Successfully installed Zsh and Oh My Zsh, and set Zsh as the default shell!{Style.RESET_ALL}")
write_log(f"Successfully installed Zsh and Oh My Zsh, and set Zsh as the default shell.")

#############################

# Install Terminal and Terminal tools, tuis and other utilities
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing terminal and utilities...{Style.RESET_ALL}")
terminal_command_list = [
    "kitty","zoxide","eza","fzf","bat","micro", "fastfetch", "fd", "ripgrep", "yazi", "btop", "bash-completion", "starship"
]
for terminal_cmd in terminal_command_list:
    print(f"{Fore.CYAN}Installing {terminal_cmd}...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", terminal_cmd, "--noconfirm", "--needed"])
    print(f"{Fore.CYAN}Successfully installed {terminal_cmd}!{Style.RESET_ALL}")
write_log(f"Successfully installed terminal and utilities: {', '.join(terminal_command_list)}.")

#############################

# Configure Starship theme by creating a configuration file at ~/.config/starship.toml with the desired theme settings
starship_config_dir = f"/home/{current_username}/.config"
if not os.path.exists(starship_config_dir):
    os.makedirs(starship_config_dir, exist_ok=True)
starship_config_path = f"{starship_config_dir}/starship.toml"

# Pass command starship preset pure-preset -o ~/.config/starship.toml to generate the configuration file with the pure-preset
run_command(["starship", "preset", "pure-preset", "-o", starship_config_path])
print(f"{Fore.CYAN}Successfully configured Starship theme with the pure-preset!{Style.RESET_ALL}")
write_log(f"Successfully configured Starship theme with the pure-preset.")

#############################

# Install Zsh plugins for autosuggestions, syntax highlighting, autocomplete, and history substring search by cloning the respective GitHub repositories into the custom plugins directory of Oh My Zsh
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Zsh plugins...{Style.RESET_ALL}")
zsh_custom_plugins_dir = f"/home/{current_username}/.oh-my-zsh/custom/plugins"

# ["zsh-autosuggestions"]="https://github.com/zsh-users/zsh-autosuggestions"
run_command(["git", "clone", "https://github.com/zsh-users/zsh-autosuggestions.git", f"{zsh_custom_plugins_dir}/zsh-autosuggestions"])

# ["zsh-syntax-highlighting"]="https://github.com/zsh-users/zsh-syntax-highlighting.git"
run_command(["git", "clone", "https://github.com/zsh-users/zsh-syntax-highlighting.git", f"{zsh_custom_plugins_dir}/zsh-syntax-highlighting"])

# ["zsh-autocomplete"]="https://github.com/marlonrichert/zsh-autocomplete.git"
run_command(["git", "clone", "https://github.com/marlonrichert/zsh-autocomplete.git", f"{zsh_custom_plugins_dir}/zsh-autocomplete"])

# ["zsh-history-substring-search"]="https://github.com/zsh-users/zsh-history-substring-search"
run_command(["git", "clone", "https://github.com/zsh-users/zsh-history-substring-search.git", f"{zsh_custom_plugins_dir}/zsh-history-substring-search"])
print(f"{Fore.CYAN}Successfully installed Zsh plugins!{Style.RESET_ALL}")
write_log(f"Successfully installed Zsh plugins: zsh-autosuggestions, zsh-syntax-highlighting, zsh-autocomplete, zsh-history-substring-search.")

#############################

# Install Neovim and LazyVim and set up the configuration with tree-sitter and LSP support and other plugins (like git integration, file explorer, etc.)
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Neovim and setting up LazyVim configuration...{Style.RESET_ALL}")
run_command(["sudo", "pacman", "-S", "neovim", "tree-sitter-cli", "--noconfirm", "--needed"])
print(f"{Fore.CYAN}Successfully installed Neovim and tree-sitter-cli!{Style.RESET_ALL}")
write_log(f"Successfully installed Neovim and tree-sitter-cli.")
# Clone the LazyVim configuration from the official LazyVim GitHub repository into the user's home directory under .config/nvim
lazyvim_config_dir = f"/home/{current_username}/.config/nvim"
if not os.path.exists(lazyvim_config_dir):
    run_command(["git", "clone", "https://github.com/LazyVim/starter", lazyvim_config_dir])
    print(f"{Fore.CYAN}Successfully cloned LazyVim configuration!{Style.RESET_ALL}")
write_log(f"Successfully cloned LazyVim configuration.")
# Remove the .git directory from the cloned LazyVim configuration to avoid issues with updates and plugin management
git_dir = os.path.join(lazyvim_config_dir, ".git")
if os.path.exists(git_dir):
    run_command(["rm", "-rf", git_dir])
    print(f"{Fore.CYAN}Removed .git directory from LazyVim configuration to avoid issues with updates and plugin management!{Style.RESET_ALL}")
write_log(f"Removed .git directory from LazyVim configuration.")
# Install the Neovim plugins using the built-in package manager and set up the configuration for tree-sitter, LSP support, and other plugins
run_command(["nvim", "--headless", "+Lazy! sync", "+qa"])
print(f"{Fore.CYAN}Successfully installed Neovim and set up LazyVim configuration with tree-sitter, LSP support, and other plugins!{Style.RESET_ALL}")
write_log(f"Successfully installed Neovim and set up LazyVim configuration with tree-sitter, LSP support, and other plugins!")

#############################

# Install mise and configure it in zshrc
# Install java@lts, dotnet@10, python@latest
# curl https://mise.run | sh
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing mise...{Style.RESET_ALL}")
run_command(["curl", "https://mise.run", "-o", "mise-install.sh"])
run_command(["sh", "mise-install.sh"])
print(f"{Fore.CYAN}Successfully installed mise!{Style.RESET_ALL}")
write_log(f"Successfully installed mise.")
# Add to zshrc and activate mise in zshrc
# run_command(["echo", 'eval "$(~/.local/bin/mise activate zsh)"', ">>", f"/home/{current_username}/.zshrc"]) 

#############################

# Take backup of existing .zshrc file and replace with the one from the current directory
print(f"{Style.BRIGHT}{Fore.YELLOW}Configuring Zsh with custom .zshrc...{Style.RESET_ALL}")
zshrc_path = f"/home/{current_username}/.zshrc"
if os.path.exists(zshrc_path):
    backup_path = f"/home/{current_username}/.zshrc.backup" + subprocess.run(["date", "+%Y%m%d-%H%M%S"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    os.rename(zshrc_path, backup_path)
    print(f"{Fore.YELLOW}Existing .zshrc file found and backed up to {backup_path}.{Style.RESET_ALL}")

run_command(["cp", "zshrc", zshrc_path])
print(f"{Fore.CYAN}Successfully configured Zsh with custom .zshrc!{Style.RESET_ALL}")
write_log(f"Successfully configured Zsh with custom .zshrc.")
# Source the zshrc to activate mise before checking
run_command(["zsh", "-c", f"source /home/{current_username}/.zshrc && which mise"])
#############################

# Add mise path to the environment variable PATH in zshrc
mise_path = f"/home/{current_username}/.local/bin/mise"
zshrc_path = f"/home/{current_username}/.zshrc"
with open(zshrc_path, "r") as f:
    zshrc_content = f.read()
# If PATH is not already set in zshrc, add it
if "PATH=$PATH:$HOME/.local/bin" not in zshrc_content:
    with open(zshrc_path, "a") as f:
        f.write(f"\nexport PATH=$PATH:$HOME/.local/bin\n")
    print(f"{Fore.CYAN}Added mise path to the environment variable PATH in .zshrc!{Style.RESET_ALL}")
    write_log(f"Added mise path to the environment variable PATH in .zshrc.")
else:
    print(f"{Fore.YELLOW}mise path is already added to the environment variable PATH in .zshrc!{Style.RESET_ALL}")
    write_log(f"mise path is already added to the environment variable PATH in .zshrc.")

# Check if mise is properly activated in the current shell by checking if the command "mise" is available and can be executed successfully
print(f"{Style.BRIGHT}{Fore.YELLOW}Checking if mise is properly activated...{Style.RESET_ALL}")
# Try checking in the default installation location
mise_path = f"/home/{current_username}/.local/bin/mise"
if os.path.exists(mise_path):
    print(f"{Fore.GREEN}mise is installed at {mise_path}!{Style.RESET_ALL}")
    write_log(f"mise is installed at {mise_path}.")
    
    # Install java@lts, dotnet@10, python@latest using mise with full path
    print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Java LTS, .NET 10, and Python latest using mise...{Style.RESET_ALL}")
    run_command([mise_path, "install", "java@lts"])
    run_command([mise_path, "install", "dotnet@10"])
    run_command([mise_path, "install", "python@latest"])
    print(f"{Fore.CYAN}Successfully installed Java LTS, .NET 10, and Python latest using mise!{Style.RESET_ALL}")
    write_log(f"Successfully installed Java LTS, .NET 10, and Python latest using mise.")
else:
    print(f"{Fore.RED}mise is not found at {mise_path}. Please check the installation.{Style.RESET_ALL}")
    write_log("mise is not found. Please check the installation.")

#############################

# Install and configure docker and docker-compose, and add the current user to the docker group to allow running docker commands without sudo
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Docker and Docker Compose...{Style.RESET_ALL}")
run_command(["sudo", "pacman", "-S", "docker", "docker-compose", "--noconfirm", "--needed"])
print(f"{Fore.CYAN}Successfully installed Docker and Docker Compose!{Style.RESET_ALL}")
write_log(f"Successfully installed Docker and Docker Compose.")
# Start the Docker service and enable it to start on boot
run_command(["sudo", "systemctl", "start", "docker"])
run_command(["sudo", "systemctl", "enable", "docker"])
print(f"{Fore.CYAN}Successfully started and enabled Docker service!{Style.RESET_ALL}")
write_log(f"Successfully started and enabled Docker service.")
# Add the current user to the docker group to allow running docker commands without sudo
run_command(["sudo", "usermod", "-aG", "docker", current_username])
print(f"{Fore.CYAN}Successfully added user {current_username} to docker group!{Style.RESET_ALL}")
write_log(f"Successfully added user {current_username} to docker group.")

#############################

# Install Lazygit and Lazydocker
print(f"{Style.BRIGHT}{Fore.YELLOW}Installing Lazygit and Lazydocker...{Style.RESET_ALL}")
run_command(["sudo", "pacman", "-S", "lazygit", "lazydocker", "--noconfirm", "--needed"])
print(f"{Fore.CYAN}Successfully installed Lazygit and Lazydocker!{Style.RESET_ALL}")
write_log(f"Successfully installed Lazygit and Lazydocker.")
# configure both in neovim and lazyvim by adding the respective plugins in snacks.nvim plugin
print(f"{Style.BRIGHT}{Fore.YELLOW}Configuring Lazygit and Lazydocker in Neovim with LazyVim...{Style.RESET_ALL}")

# Call neoviminit.sh to inject the lazygit and lazydocker configuration in snacks.nvim
# In case of errors, handle them gracefully and log the errors to the log file
result = run_command(["sh", "neovimInit.sh"])
if result.returncode != 0:
    print(f"{Fore.RED}Error configuring Lazygit and Lazydocker in Neovim with LazyVim: {result.stderr}{Style.RESET_ALL}")
    write_log(f"Error configuring Lazygit and Lazydocker in Neovim with LazyVim: {result.stderr}")
else:
    print(f"{Fore.CYAN}Successfully configured Lazygit and Lazydocker in Neovim with LazyVim!{Style.RESET_ALL}")
    write_log(f"Successfully configured Lazygit and Lazydocker in Neovim with LazyVim.")

#############################

# Check if flatpak is installed, and if not, install it and add flathub repository
print(f"{Style.BRIGHT}{Fore.YELLOW}Checking for Flatpak installation...{Style.RESET_ALL}")
flatpak_check = subprocess.run(["which", "flatpak"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if flatpak_check.returncode != 0:
    print(f"{Fore.YELLOW}Flatpak is not installed. Installing Flatpak...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", "flatpak", "--noconfirm", "--needed"])
    print(f"{Fore.CYAN}Successfully installed Flatpak!{Style.RESET_ALL}")
    write_log("Successfully installed Flatpak.")
    # Add flathub repository for flatpak
    run_command(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"])
    print(f"{Fore.CYAN}Successfully added Flathub repository for Flatpak!{Style.RESET_ALL}")
    write_log("Successfully added Flathub repository for Flatpak.")
else:
    print(f"{Fore.GREEN}Flatpak is already installed at {flatpak_check.stdout.strip()}!{Style.RESET_ALL}")
    write_log(f"Flatpak is already installed at {flatpak_check.stdout.strip()}.")
    # Check if flathub repository is already added for flatpak, and if not, add it
    flathub_check = subprocess.run(["flatpak", "remotes"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if "flathub" not in flathub_check.stdout:
        run_command(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"])
        print(f"{Fore.CYAN}Successfully added Flathub repository for Flatpak!{Style.RESET_ALL}")
        write_log("Successfully added Flathub repository for Flatpak.")
    else:
        print(f"{Fore.GREEN}Flathub repository is already added for Flatpak!{Style.RESET_ALL}")
        write_log("Flathub repository is already added for Flatpak.")

#############################

# Prepare a list of native arch (pacman or yay) applications to install
# User to select multiple app numbers from the list or all and install the selected applications
print(f"{Style.BRIGHT}{Fore.YELLOW}Preparing list of native applications to install...{Style.RESET_ALL}")
native_apps = [
    "firefox","vlc","virtualbox","handbrake","qbittorrent","toolbox","distrobox","libreoffice-fresh", "featherpad", "foliate"
]
print(f"{Fore.CYAN}Native applications to consider for installation: {', '.join(native_apps)}{Style.RESET_ALL}")
write_log(f"Prepared list of native applications to install: {', '.join(native_apps)}.")
# User input to select multiple app numbers from the list or all and install the selected applications
print(f"{Style.BRIGHT}{Fore.YELLOW}Please select the applications you want to install by entering the corresponding numbers separated by commas, or enter 'all' to install all applications:{Style.RESET_ALL}")
for i, app in enumerate(native_apps):
    print(f"{Fore.CYAN}{i+1}. {app}{Style.RESET_ALL}")
user_selection = get_user_input("Your selection: ")
if user_selection.lower() == "all":
    selected_apps = native_apps
else:
    selected_indices = [int(x.strip()) - 1 for x in user_selection.split(",") if x.strip().isdigit() and 0 < int(x.strip()) <= len(native_apps)]
    selected_apps = [native_apps[i] for i in selected_indices]
print(f"{Fore.CYAN}You have selected the following applications for installation: {', '.join(selected_apps)}{Style.RESET_ALL}")
write_log(f"User selected the following applications for installation: {', '.join(selected_apps)}.")
# Install the selected applications using pacman or yay
for app in selected_apps:
    print(f"{Fore.CYAN}Installing {app}...{Style.RESET_ALL}")
    run_command(["sudo", "pacman", "-S", app, "--noconfirm", "--needed"])
    write_log(f"Successfully installed {app}.")

#############################

# Install visual studio code using yay 
print(f"{Fore.CYAN}Installing Visual Studio Code...{Style.RESET_ALL}")
run_command(["yay", "-S", "visual-studio-code-bin", "--noconfirm", "--needed"])
write_log("Successfully installed Visual Studio Code.")

# Install chrome using yay
print(f"{Fore.CYAN}Installing Google Chrome...{Style.RESET_ALL}")
run_command(["yay", "-S", "google-chrome", "--noconfirm", "--needed"])
write_log("Successfully installed Google Chrome.")

#############################

# Replace the kitty terminal configuration file with the one from the current directory
print(f"{Style.BRIGHT}{Fore.YELLOW}Configuring Kitty terminal...{Style.RESET_ALL}")
kitty_config_dir = f"/home/{current_username}/.config/kitty"
if not os.path.exists(kitty_config_dir):
    os.makedirs(kitty_config_dir, exist_ok=True)
kitty_config_path = f"{kitty_config_dir}/kitty.conf"
if os.path.exists(kitty_config_path):
    backup_path = f"{kitty_config_path}.backup" + subprocess.run(["date", "+%Y%m%d-%H%M%S"], check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    os.rename(kitty_config_path, backup_path)
    print(f"{Fore.YELLOW}Existing kitty.conf file found and backed up to {backup_path}.{Style.RESET_ALL}")
run_command(["cp", "kitty.conf", kitty_config_path])
print(f"{Fore.CYAN}Successfully configured Kitty terminal!{Style.RESET_ALL}")
write_log("Successfully configured Kitty terminal.")
# Copy the current-theme.conf file from the current directory to the kitty configuration directory
current_theme_path = f"{kitty_config_dir}/current-theme.conf"
run_command(["cp", "current-theme.conf", current_theme_path])
print(f"{Fore.CYAN}Successfully copied current-theme.conf to Kitty configuration directory!{Style.RESET_ALL}")
write_log("Successfully copied current-theme.conf to Kitty configuration directory.")

#############################

# Check if desktop environment is GNOME, if yes the call local script to configure gnome settings and extensions and keybindings
print(f"{Style.BRIGHT}{Fore.YELLOW}Checking for desktop environment...{Style.RESET_ALL}")
desktop_env_check = os.environ.get("XDG_CURRENT_DESKTOP", "")
if "GNOME" in desktop_env_check:
    print(f"{Fore.GREEN}GNOME desktop environment detected! Configuring GNOME settings, extensions, and keybindings...{Style.RESET_ALL}")
    write_log("GNOME desktop environment detected. Configuring GNOME settings, extensions, and keybindings.")
    result = run_command(["sh", "gnomeConfig.sh"])
    if result.returncode != 0:
        print(f"{Fore.RED}Error configuring GNOME: {result.stderr}{Style.RESET_ALL}")
        write_log(f"Error configuring GNOME: {result.stderr}")
    else:
        print(f"{Fore.CYAN}Successfully configured GNOME settings, extensions, and keybindings!{Style.RESET_ALL}")
        write_log("Successfully configured GNOME settings, extensions, and keybindings.")
else:
    print(f"{Fore.YELLOW}No GNOME desktop environment detected. Skipping GNOME configuration.{Style.RESET_ALL}")
    write_log("No GNOME desktop environment detected. Skipping GNOME configuration.")

# Clean up
run_command(["sudo", "pacman", "-Sc", "--noconfirm"])

# Final message
print(f"{Style.BRIGHT}{Fore.GREEN}Arch Linux setup script completed successfully! Please restart your system to apply all changes and enjoy your new Arch Linux setup!{Style.RESET_ALL}")
result = get_user_input("Do you want to restart now? (y/n): ")
if result.lower() == "y":
    run_command(["sudo", "reboot"])


