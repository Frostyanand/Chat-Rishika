#!/usr/bin/env python
"""
Installation script for Elysia.

This script performs a clean installation of the Elysia chatbot
by cleaning up existing artifacts and setting up the project.
"""

import os
import sys
import shutil
import subprocess
import time
import importlib.util

def check_dependencies():
    """Check if required dependencies are installed."""
    required = ["setuptools", "wheel", "pip"]
    missing = []
    
    for package in required:
        if importlib.util.find_spec(package) is None:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def clean_build_artifacts():
    """Clean up build artifacts."""
    print("Cleaning up build artifacts...")
    
    # Directories to remove
    artifacts = ["build", "dist", "elysia_chatbot.egg-info", ".venv"]
    
    # First try to remove them directly
    for artifact in artifacts:
        if os.path.exists(artifact):
            try:
                if os.path.isdir(artifact):
                    shutil.rmtree(artifact)
                else:
                    os.remove(artifact)
                print(f"Removed {artifact}")
            except Exception as e:
                print(f"Could not remove {artifact}: {e}")
    
    # Clean __pycache__ directories
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                try:
                    pycache_path = os.path.join(root, dir_name)
                    shutil.rmtree(pycache_path)
                    print(f"Removed {pycache_path}")
                except Exception as e:
                    print(f"Could not remove {pycache_path}: {e}")

def create_misc_dir():
    """Create Misc directory if it doesn't exist."""
    misc_dir = "Misc"
    if not os.path.exists(misc_dir):
        os.makedirs(misc_dir)
        print(f"Created {misc_dir} directory")

def install_package():
    """Install the package in development mode."""
    print("\nInstalling Elysia in development mode...")
    
    # Try regular pip install (development mode)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("Installation successful!")
        return True
    except subprocess.CalledProcessError:
        print("Development installation failed, trying regular installation...")
    
    # If development mode fails, try regular install
    try:
        subprocess.check_call([sys.executable, "setup.py", "install"])
        print("Installation successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False

def main():
    """Main function to install Elysia."""
    print("=" * 60)
    print("Elysia Installation")
    print("=" * 60)
    
    # Check dependencies
    check_dependencies()
    
    # Clean up
    clean_build_artifacts()
    
    # Create Misc directory
    create_misc_dir()
    
    # Wait a moment to ensure files are released
    time.sleep(1)
    
    # Install package
    success = install_package()
    
    if success:
        print("\nElysia has been installed successfully!")
        print("\nTo run the chatbot, use:")
        print("python chatbot.py")
    else:
        print("\nInstallation encountered errors. Please check the output above.")
        print("You can still run the chatbot directly without installation:")
        print("python chatbot.py")
    
    print("\nAll build artifacts have been organized in the Misc directory.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation interrupted.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 