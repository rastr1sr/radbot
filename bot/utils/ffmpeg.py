import os
import platform
import subprocess
import tempfile
import shutil
import stat
import urllib.request
import zipfile
import tarfile
import logging

from bot.utils.logger import get_logger

logger = get_logger("FFmpegInstaller")

def is_ffmpeg_installed() -> bool:
    """Check if FFmpeg is available in PATH."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def install_ffmpeg_windows() -> bool:
    """Download and install FFmpeg for Windows."""
    try:
        temp_dir = tempfile.mkdtemp()
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        logger.info(f"Downloading FFmpeg from {ffmpeg_url}...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        bin_dir = None
        for root, dirs, files in os.walk(temp_dir):
            if "ffmpeg.exe" in files:
                bin_dir = root
                break
        if not bin_dir:
            logger.error("Could not find ffmpeg.exe in the extracted files")
            return False
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_dir = os.path.join(script_dir, "ffmpeg")
        os.makedirs(ffmpeg_dir, exist_ok=True)
        for exe in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
            exe_path = os.path.join(bin_dir, exe)
            if os.path.exists(exe_path):
                shutil.copy(exe_path, ffmpeg_dir)
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
        shutil.rmtree(temp_dir)
        if is_ffmpeg_installed():
            logger.info(f"FFmpeg successfully installed to {ffmpeg_dir}")
            logger.info("Note: You may need to add this directory to your PATH permanently")
            return True
        else:
            logger.error("FFmpeg installation failed verification")
            return False
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {e}")
        return False

def install_ffmpeg_linux() -> bool:
    """Install FFmpeg using the appropriate package manager for Linux."""
    try:
        if shutil.which("apt-get"):
            cmd = ["sudo", "apt-get", "update"]
            subprocess.run(cmd, check=True)
            cmd = ["sudo", "apt-get", "install", "-y", "ffmpeg"]
        elif shutil.which("yum"):
            cmd = ["sudo", "yum", "install", "-y", "ffmpeg"]
        elif shutil.which("dnf"):
            cmd = ["sudo", "dnf", "install", "-y", "ffmpeg"]
        elif shutil.which("pacman"):
            cmd = ["sudo", "pacman", "-S", "--noconfirm", "ffmpeg"]
        else:
            logger.error("Unsupported Linux distribution or package manager not found")
            return False
        logger.info(f"Installing FFmpeg using: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        if is_ffmpeg_installed():
            logger.info("FFmpeg successfully installed")
            return True
        else:
            logger.error("FFmpeg installation failed verification")
            return False
    except subprocess.SubprocessError as e:
        logger.error(f"Error installing FFmpeg: {e}")
        logger.error("You may need to install FFmpeg manually")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing FFmpeg: {e}")
        return False

def install_ffmpeg_macos() -> bool:
    """Install FFmpeg using Homebrew on macOS."""
    try:
        if not shutil.which("brew"):
            logger.error("Homebrew not found. Please install Homebrew first: https://brew.sh/")
            return False
        logger.info("Installing FFmpeg using Homebrew...")
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        if is_ffmpeg_installed():
            logger.info("FFmpeg successfully installed")
            return True
        else:
            logger.error("FFmpeg installation failed verification")
            return False
    except subprocess.SubprocessError as e:
        logger.error(f"Error installing FFmpeg: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error installing FFmpeg: {e}")
        return False

def check_and_install_ffmpeg() -> bool:
    """Check if FFmpeg is installed; if not, attempt to install it."""
    logger.info("Checking FFmpeg installation...")
    if is_ffmpeg_installed():
        logger.info("FFmpeg is already installed and accessible.")
        return True
    logger.warning("FFmpeg not found. Attempting to install...")
    system = platform.system().lower()
    if system == "windows":
        return install_ffmpeg_windows()
    elif system == "linux":
        return install_ffmpeg_linux()
    elif system == "darwin":
        return install_ffmpeg_macos()
    else:
        logger.error(f"Unsupported operating system: {system}")
        return False
