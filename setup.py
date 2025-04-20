#!/usr/bin/env python3
"""
setup.py - Unified setup and installation script for Elysia

This script handles all aspects of setting up the Elysia chatbot system:
1. Cleans up existing build artifacts
2. Sets up necessary directories
3. Installs all dependencies
4. Downloads required data for NLP components
5. Configures the environment for running Elysia

Run with: python setup.py install
"""
import os
import re
import sys
import shutil
import time
import subprocess
import importlib.util
from setuptools import setup, find_packages

# Create Misc directory for build artifacts
MISC_DIR = "Misc"
if not os.path.exists(MISC_DIR):
    os.makedirs(MISC_DIR)
    print(f"Created {MISC_DIR} directory")

# Set build directories to be inside Misc folder
os.environ['PYTHONUSERBASE'] = os.path.abspath(MISC_DIR)
build_dir = os.path.join(MISC_DIR, "build")
dist_dir = os.path.join(MISC_DIR, "dist")
egg_info_dir = os.path.join(MISC_DIR, "elysia_chatbot.egg-info")

def print_section(title):
    """Print a section title with formatting."""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are installed."""
    print_section("Checking Dependencies")
    required = ["setuptools", "wheel", "pip"]
    missing = []
    
    for package in required:
        if importlib.util.find_spec(package) is None:
            missing.append(package)
    
    if missing:
        print(f"Missing required packages: {', '.join(missing)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
    else:
        print("All basic dependencies are installed.")

def clean_build_artifacts():
    """Clean up build artifacts."""
    print_section("Cleaning Build Artifacts")
    
    # Directories to remove
    artifacts = ["build", "dist", "elysia_chatbot.egg-info", "__pycache__"]
    
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

def get_version():
    """Get the version from the package."""
    init_file = os.path.join("memory_management", "__init__.py")
    if os.path.exists(init_file):
        with open(init_file, "r") as f:
            content = f.read()
            match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content, re.MULTILINE)
            if match:
                return match.group(1)
    return "0.1.0"  # Default version if not found

def ensure_init_files():
    """Create __init__.py files if they don't exist."""
    print_section("Setting Up Package Structure")
    
    # Ensure api_layer has an __init__.py file
    if not os.path.exists(os.path.join("api_layer", "__init__.py")):
        with open(os.path.join("api_layer", "__init__.py"), "w") as f:
            f.write('"""Elysia API layer package."""\n\n__version__ = "0.1.0"\n')
        print("Created api_layer/__init__.py")
    
    # Create __init__.py files for other packages
    for pkg in ["memory_management", "personality_layer"]:
        init_file = os.path.join(pkg, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write(f'"""Elysia {pkg} package."""\n\n__version__ = "0.1.0"\n')
            print(f"Created {init_file}")

def download_nltk_data():
    """Download NLTK data for NLP components."""
    print_section("Setting Up NLP Components - NLTK")
    nltk_dir = os.path.join(MISC_DIR, "nltk_data")
    if not os.path.exists(nltk_dir):
        os.makedirs(nltk_dir)
    
    try:
        import nltk
        print(f"Downloading NLTK data to {nltk_dir}...")
        nltk.download('punkt', quiet=True, download_dir=nltk_dir)
        nltk.download('stopwords', quiet=True, download_dir=nltk_dir)
        nltk.download('wordnet', quiet=True, download_dir=nltk_dir)
        
        # Set NLTK_DATA environment variable
        os.environ['NLTK_DATA'] = nltk_dir
        print("NLTK data downloaded successfully")
    except ImportError:
        print("NLTK not installed yet. Will download data after installation.")

def download_spacy_model():
    """Download spaCy model for NLP components."""
    print_section("Setting Up NLP Components - spaCy")
    spacy_dir = os.path.join(MISC_DIR, "spacy_models")
    if not os.path.exists(spacy_dir):
        os.makedirs(spacy_dir)
    
    try:
        import spacy
        try:
            spacy.load('en_core_web_sm')
            print("spaCy model already installed.")
        except OSError:
            print(f"Downloading spaCy model to {spacy_dir}...")
            # Set environment variable to store models in Misc directory
            env = os.environ.copy()
            env['SPACY_DATA'] = spacy_dir
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], env=env)
            print("spaCy model downloaded successfully")
    except ImportError:
        print("spaCy not installed yet. Will download model after installation.")

def setup_environment():
    """Set up the local development environment."""
    print_section("Setting Up Environment")
    
    # Backup important files
    backup_dir = os.path.join(MISC_DIR, "backup")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Backup chatbot.py
    if os.path.exists("chatbot.py"):
        shutil.copy("chatbot.py", os.path.join(backup_dir, "chatbot.py.bak"))
        print("Backed up chatbot.py")

# Core requirements
requirements = [
    # Networking
    "requests>=2.25.1",
    
    # Encryption
    "cryptography>=39.0.0",
    
    # CLI
    "colorama>=0.4.4",
    
    # Utilities
    "python-dateutil>=2.8.2",
    "jsonschema>=4.0.0",
    "nltk>=3.7.0",
    "spacy>=3.5.0",
    "pytz>=2022.7"
]

# Development requirements
dev_requirements = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
    "flake8>=6.0.0"
]

def run_setup():
    """Run the setuptools setup function."""
    # Read long description from README
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except FileNotFoundError:
        long_description = "Elysia - An emotionally intelligent AI companion"
    
    package_data = {
        "": ["*.json", "*.txt", "*.md"],
        "memory_management": ["*.json", "*.txt"],
        "personality_layer": ["*.json", "response_templates/*.py"],
        "api_layer": ["*.py"]
    }
    
    setup(
        name="elysia-chatbot",
        version=get_version(),
        author="Elysia Team",
        author_email="info@elysia-chatbot.com",
        description="Elysia - An emotionally intelligent AI companion",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/elysia/chatbot",
        packages=find_packages(include=[
            "memory_management", "memory_management.*", 
            "personality_layer", "personality_layer.*",
            "api_layer", "api_layer.*"
        ]),
        py_modules=["chatbot"],  # Include chatbot.py as a module
        include_package_data=True,
        package_data=package_data,
        install_requires=requirements,
        extras_require={
            "dev": dev_requirements,
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: End Users/Desktop",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Communications :: Chat",
        ],
        python_requires=">=3.8",
        entry_points={
            "console_scripts": [
                "elysia=chatbot:main",
            ],
        },
    )

def main():
    """Main function to orchestrate the setup process."""
    print_section("Elysia Setup and Installation")
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # If no arguments provided, assume install
        sys.argv.append("install")
    
    # Check for clean command
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_build_artifacts()
        print("\nCleanup completed.")
        sys.exit(0)
    
    # Regular setup process
    try:
        # Step 1: Check dependencies
        check_dependencies()
        
        # Step 2: Clean build artifacts
        clean_build_artifacts()
        
        # Step 3: Ensure directory structure
        ensure_init_files()
        
        # Step 4: Set up environment
        setup_environment()
        
        # Step 5: Download NLP data
        try:
            download_nltk_data()
            download_spacy_model()
        except Exception as e:
            print(f"Warning: Could not download NLP data: {e}")
            print("You may need to download it manually after installation.")
        
        # Step 6: Run setuptools setup
        run_setup()
        
        print_section("Installation Complete")
        print("Elysia has been successfully installed!")
        print("\nTo run the chatbot, use:")
        print("python chatbot.py")
        
    except KeyboardInterrupt:
        print("\nSetup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 