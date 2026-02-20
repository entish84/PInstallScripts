#!/usr/bin/env python3

import os
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# --- Color Handling (Optional Colorama Fallback) ---
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback to standard ANSI escape codes if colorama is missing
    class Fore:
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        CYAN = "\033[36m"
        RESET = "\033[39m"
    class Style:
        NORMAL = ""
        BRIGHT = "\033[1m"
        RESET_ALL = "\033[0m"
    # Create a dummy init function
    def init(autoreset=False): pass

# --- Logging Setup ---
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "arch-pi-script.log"

# Log rotation: rename existing log to keep history
if LOG_FILE.exists():
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    LOG_FILE.rename(LOG_FILE.with_name(f"{LOG_FILE.name}_{timestamp}"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE)]
)
logger = logging.getLogger("arch_setup")

def write_log(message, level=logging.INFO):
    if level == logging.INFO: logger.info(message)
    elif level == logging.ERROR: logger.error(message)
    elif level == logging.WARNING: logger.warning(message)

def print_status(message, color=Fore.CYAN, style=Style.NORMAL):
    print(f"{style}{color}{message}{Style.RESET_ALL}")
    write_log(message)

def print_error(message):
    print(f"{Style.BRIGHT}{Fore.RED}ERROR: {message}{Style.RESET_ALL}")
    write_log(message, logging.ERROR)

def run_command(command, shell=False, check=True, user=None):
    """Run a command with proper logging and optional user switching."""
    if user and user != "root":
        if isinstance(command, list):
            command = ["sudo", "-u", user] + command
        else:
            command = f"sudo -u {user} {command}"

    try:
        result = subprocess.run(
            command, shell=shell, check=check,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stdout:
            write_log(f"CMD Output: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}\nError: {e.stderr}")
        return e

def get_real_user():
    """Detect the actual user even if running under sudo."""
    return os.environ.get("SUDO_USER") or os.environ.get("USER") or "default_user"

def get_user_home(username):
    """Get the absolute path to the user's home directory."""
    return Path(os.path.expanduser(f"~{username}"))

def check_preflights():
    """Verify required helper scripts and configs exist before starting."""
    required = ["zshInstall.sh", "neovimInit.sh", "gnomeConfig.sh", "gnomeExtensions.sh", "zshrc", "kitty.conf", "current-theme.conf"]
    missing = [f for f in required if not Path(f).exists()]
    if missing:
        print_error(f"Missing required files in script directory: {', '.join(missing)}")
        return False
    return True

# --- Setup Tasks ---

def update_system():
    print_status("\n>>> Updating System and AUR Packages", Fore.YELLOW, Style.BRIGHT)
    run_command(["sudo", "pacman", "-Syu", "--noconfirm"])
    
    # Check for yay and install if missing
    if run_command(["which", "yay"], check=False).returncode != 0:
        print_status("yay not found. Installing yay...", Fore.YELLOW)
        run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "git", "base-devel"])
        # Install yay from AUR
        run_command("git clone https://aur.archlinux.org/yay.git /tmp/yay && cd /tmp/yay && makepkg -si --noconfirm", shell=True)
    
    run_command(["yay", "-Syu", "--noconfirm"])

def install_dev_tools():
    print_status("\n>>> Installing Essential Development Tools", Fore.YELLOW, Style.BRIGHT)
    tools = [
        "base-devel", "git", "gcc", "make", "clang", "cargo", "just", 
        "curl", "wget", "unzip", "unrar", "p7zip", "xclip", "wl-clipboard"
    ]
    run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + tools)

def configure_git():
    print_status("\n>>> Configuring Git Settings", Fore.YELLOW, Style.BRIGHT)
    
    is_test = input(f"{Fore.YELLOW}Use default test Git config? (y/n): {Style.RESET_ALL}").lower() == 'y'
    
    name = "entish84" if is_test else input(f"{Fore.YELLOW}Enter Git Name: {Style.RESET_ALL}").strip()
    email = "entishthoughts@outlook.com" if is_test else input(f"{Fore.YELLOW}Enter Git Email: {Style.RESET_ALL}").strip()
    
    run_command(["git", "config", "--global", "user.name", name])
    run_command(["git", "config", "--global", "user.email", email])
    print_status(f"Git Configured: {name} <{email}>")
    return email

def setup_ssh(user, email):
    print_status("\n>>> Generating SSH Keys and Setting Up Agent", Fore.YELLOW, Style.BRIGHT)
    home = get_user_home(user)
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    
    key_path = ssh_dir / "id_ed25519"
    if not key_path.exists():
        run_command(["ssh-keygen", "-t", "ed25519", "-C", email, "-f", str(key_path), "-N", ""], user=user)
        print_status(f"Generated new ED25519 key at {key_path}")
    else:
        print_status(f"SSH key already exists at {key_path}, skipping generation.")

    # Attempt to add to agent
    run_command("eval $(ssh-agent -s) && ssh-add " + str(key_path), shell=True, check=False, user=user)
    
    pub_key_file = Path(f"{key_path}.pub")
    if pub_key_file.exists():
        pub_key = pub_key_file.read_text().strip()
        os.environ["GITPUBKEY"] = pub_key
        print_status("Public Key added to environment variable GITPUBKEY.")

def install_fonts():
    print_status("\n>>> Installing Nerd Fonts and Typography", Fore.YELLOW, Style.BRIGHT)
    fonts = ["inter-font", "ttf-jetbrains-mono-nerd", "ttf-firacode-nerd"]
    run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + fonts)

def setup_zsh(user):
    print_status("\n>>> Installing Zsh and Oh-My-Zsh", Fore.YELLOW, Style.BRIGHT)
    run_command(["sh", "zshInstall.sh"], user=user)
    
    # Add ssh-agent plugin if not present
    home = get_user_home(user)
    zshrc = home / ".zshrc"
    if zshrc.exists():
        content = zshrc.read_text()
        if "plugins=(" in content and "ssh-agent" not in content:
            print_status("Adding ssh-agent plugin to .zshrc")
            new_content = content.replace("plugins=(", "plugins=(ssh-agent ")
            zshrc.write_text(new_content)

def setup_starship(user):
    print_status("\n>>> Configuring Starship Shell Prompt", Fore.YELLOW, Style.BRIGHT)
    config_dir = get_user_home(user) / ".config"
    config_dir.mkdir(parents=True, exist_ok=True)
    run_command(["starship", "preset", "pure-preset", "-o", str(config_dir / "starship.toml")], user=user)

def setup_neovim(user):
    print_status("\n>>> Installing Neovim and Starter Config", Fore.YELLOW, Style.BRIGHT)
    run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "neovim", "tree-sitter-cli"])
    
    home = get_user_home(user)
    nvim_dir = home / ".config" / "nvim"
    if not nvim_dir.exists():
        run_command(["git", "clone", "https://github.com/LazyVim/starter", str(nvim_dir)], user=user)
        # Remove git dir to avoid conflicts with future updates
        run_command(["rm", "-rf", str(nvim_dir / ".git")], user=user)
    
    # Run the init script for extra configs (plugins, LSPs)
    run_command(["sh", "neovimInit.sh"], user=user)
    # Sync plugins in headless mode
    run_command(["nvim", "--headless", "+Lazy! sync", "+qa"], user=user)

def setup_mise(user):
    print_status("\n>>> Installing Mise Version Manager", Fore.YELLOW, Style.BRIGHT)
    run_command("curl https://mise.run | sh", shell=True, user=user)
    
    home = get_user_home(user)
    zshrc = home / ".zshrc"
    mise_bin = home / ".local" / "bin" / "mise"
    
    # Ensure mise is in path and activated in .zshrc
    if zshrc.exists():
        content = zshrc.read_text()
        updates = []
        if 'PATH=$PATH:$HOME/.local/bin' not in content:
            updates.append('export PATH=$PATH:$HOME/.local/bin')
        if 'eval "$(~/.local/bin/mise activate zsh)"' not in content:
            updates.append('eval "$(~/.local/bin/mise activate zsh)"')
        
        if updates:
            with zshrc.open("a") as f:
                f.write("\n# Mise Activation\n" + "\n".join(updates) + "\n")
    
    if mise_bin.exists():
        for tool in ["java@lts", "dotnet@10", "python@latest"]:
            print_status(f"Mise: Installing {tool}")
            run_command([str(mise_bin), "use", "--global", tool], user=user)

def setup_docker(user):
    print_status("\n>>> Setting Up Docker Environment", Fore.YELLOW, Style.BRIGHT)
    run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm", "docker", "docker-compose"])
    run_command(["sudo", "systemctl", "enable", "--now", "docker"])
    run_command(["sudo", "usermod", "-aG", "docker", user])

def setup_apps(user):
    print_status("\n>>> Installing Terminal Utilities and Desktop Apps", Fore.YELLOW, Style.BRIGHT)
    utils = [
        "kitty", "zoxide", "eza", "fzf", "bat", "micro", "fastfetch", "fd", 
        "ripgrep", "yazi", "btop", "bash-completion", "starship", 
        "lazygit", "lazydocker", "flatpak"
    ]
    run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + utils)
    
    # Enable Flathub
    run_command(["sudo", "flatpak", "remote-add", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"])
    
    # Interactive Application Selection
    apps = ["firefox", "vlc", "virtualbox", "handbrake", "qbittorrent", "toolbox", "distrobox", "libreoffice-fresh", "featherpad", "foliate"]
    print(f"\n{Style.BRIGHT}{Fore.YELLOW}Select native applications to install (e.g., 1,2,5 or 'all'):{Style.RESET_ALL}")
    for i, app in enumerate(apps, 1):
        print(f"{i}. {app}")
    
    choice = input(f"{Fore.GREEN}Your choice: {Style.RESET_ALL}").strip().lower()
    if choice == 'all':
        selected = apps
    else:
        try:
            selected = [apps[int(i.strip())-1] for i in choice.split(",") if i.strip().isdigit() and 0 < int(i.strip()) <= len(apps)]
        except (ValueError, IndexError):
            print_status("Invalid selection detected, skipping additional apps.", Fore.YELLOW)
            selected = []
    
    if selected:
        run_command(["sudo", "pacman", "-S", "--needed", "--noconfirm"] + selected)

    # AUR Tools
    print_status("Installing popular AUR packages...")
    run_command(["yay", "-S", "--needed", "--noconfirm", "visual-studio-code-bin", "google-chrome"])

def setup_configs(user):
    print_status("\n>>> Finalizing Tool Configurations", Fore.YELLOW, Style.BRIGHT)
    home = get_user_home(user)
    
    # Kitty Terminal Config
    kitty_dir = home / ".config" / "kitty"
    kitty_dir.mkdir(parents=True, exist_ok=True)
    run_command(["cp", "kitty.conf", str(kitty_dir / "kitty.conf")], user=user)
    run_command(["cp", "current-theme.conf", str(kitty_dir / "current-theme.conf")], user=user)
    
    # GNOME Settings
    is_gnome = "GNOME" in os.environ.get("XDG_CURRENT_DESKTOP", "")
    if not is_gnome:
        # Fallback check: is gnome-shell installed and gsettings available?
        has_gnome_shell = subprocess.run(["which", "gnome-shell"], capture_output=True).returncode == 0
        has_gsettings = subprocess.run(["which", "gsettings"], capture_output=True).returncode == 0
        if has_gnome_shell and has_gsettings:
            is_gnome = True

    if is_gnome:
        print_status("GNOME environment detected, applying UI tweaks...")
        run_command(["sh", "gnomeConfig.sh"], user=user)
        run_command(["sh", "gnomeExtensions.sh"], user=user)

def main():
    if not check_preflights(): return
    
    user = get_real_user()
    print_status(f"Starting Arch Linux Post-Install Setup for: {user}", Fore.GREEN, Style.BRIGHT)
    
    update_system()
    install_dev_tools()
    email = configure_git()
    setup_ssh(user, email)
    install_fonts()
    setup_zsh(user)
    setup_starship(user)
    setup_neovim(user)
    setup_mise(user)
    setup_docker(user)
    setup_apps(user)
    setup_configs(user)
    
    # Cleanup pacman cache
    run_command(["sudo", "pacman", "-Sc", "--noconfirm"])
    print_status("\nSetup Completed Successfully!", Fore.GREEN, Style.BRIGHT)
    print_status("It is highly recommended to restart your system now.")
    
    if input(f"{Fore.YELLOW}Reboot now? (y/n): {Style.RESET_ALL}").lower() == 'y':
        run_command(["sudo", "reboot"])

if __name__ == "__main__":
    main()
