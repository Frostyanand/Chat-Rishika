"""
Setup script for the Elysia chatbot.

This script installs the Elysia chatbot and all required dependencies.
"""
import os
import re
import sys
import shutil
from setuptools import setup, find_packages


# Create Misc directory if it doesn't exist
MISC_DIR = "Misc"
if not os.path.exists(MISC_DIR):
    os.makedirs(MISC_DIR)

# Set build directories to be inside Misc folder
os.environ['PYTHONUSERBASE'] = os.path.abspath(MISC_DIR)
build_dir = os.path.join(MISC_DIR, "build")
dist_dir = os.path.join(MISC_DIR, "dist")
egg_info_dir = os.path.join(MISC_DIR, "elysia_chatbot.egg-info")


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


# Read long description from README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Elysia - An emotionally intelligent AI companion"

# Core requirements
requirements = [
    # Removed database-related dependencies
    
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

# Cleanup function to remove unwanted files/folders
def cleanup_artifacts():
    """Remove build artifacts from the main directory"""
    artifacts = ["build", "dist", "elysia_chatbot.egg-info", "__pycache__"]
    for artifact in artifacts:
        if os.path.exists(artifact):
            if os.path.isdir(artifact):
                shutil.rmtree(artifact)
            else:
                os.remove(artifact)
    print("Cleaned up build artifacts from main directory")

# Check if cleanup is requested
if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
    cleanup_artifacts()
    sys.exit(0)

# Create a simple Python file to make the packages importable
for pkg in ["memory_management", "personality_layer"]:
    init_file = os.path.join(pkg, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write(f'"""Elysia {pkg} package."""\n\n__version__ = "0.1.0"\n')
        print(f"Created {init_file}")

# Download NLTK data if not already downloaded
try:
    import nltk
    nltk.download('punkt', quiet=True, download_dir=os.path.join(MISC_DIR, "nltk_data"))
    nltk.download('stopwords', quiet=True, download_dir=os.path.join(MISC_DIR, "nltk_data"))
    nltk.download('wordnet', quiet=True, download_dir=os.path.join(MISC_DIR, "nltk_data"))
    # Set NLTK_DATA environment variable
    os.environ['NLTK_DATA'] = os.path.join(MISC_DIR, "nltk_data")
except ImportError:
    print("NLTK not installed yet. Will attempt to download data after installation.")


def download_nltk_data():
    """Helper function to download NLTK data if needed."""
    nltk_dir = os.path.join(MISC_DIR, "nltk_data")
    if not os.path.exists(nltk_dir):
        os.makedirs(nltk_dir)
    
    import nltk
    nltk.download('punkt', download_dir=nltk_dir)
    nltk.download('stopwords', download_dir=nltk_dir)
    nltk.download('wordnet', download_dir=nltk_dir)
    
    # Set NLTK_DATA environment variable
    os.environ['NLTK_DATA'] = nltk_dir


# Download spaCy model if not already downloaded
def download_spacy_model():
    """Helper function to download spaCy model if needed."""
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
            import subprocess
            # Set environment variable to store models in Misc directory
            env = os.environ.copy()
            env['SPACY_DATA'] = spacy_dir
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], env=env)
    except ImportError:
        print("spaCy not installed yet. Will attempt to download model after installation.")


class PostInstallCommand(object):
    """Post-installation command to download needed data."""
    
    def run(self):
        """Run post-install steps."""
        try:
            download_nltk_data()
            download_spacy_model()
        except Exception as e:
            print(f"Error downloading data: {e}")

# Copy the main chatbot.py file to make it directly usable
if os.path.exists("chatbot.py"):
    if not os.path.exists(os.path.join(MISC_DIR, "backup")):
        os.makedirs(os.path.join(MISC_DIR, "backup"))
    shutil.copy("chatbot.py", os.path.join(MISC_DIR, "backup", "chatbot.py.bak"))

package_data = {
    "": ["*.json", "*.txt", "*.md"],
    "memory_management": ["*.json", "*.txt"],  # Removed *.sql
    "personality_layer": ["*.json", "response_templates/*.py"]
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
    packages=find_packages(include=["memory_management", "memory_management.*", 
                                   "personality_layer", "personality_layer.*"]),
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
    # Set custom build directories
    options={
        'build': {'build_base': build_dir},
        'build_ext': {'build_lib': build_dir},
        'egg_info': {'egg_base': MISC_DIR},
        'bdist': {'dist_dir': dist_dir},
        'bdist_wheel': {'dist_dir': dist_dir},
    },
)

# Attempt to download data after installation
if "install" in sys.argv:
    try:
        PostInstallCommand().run()
    except Exception as e:
        print(f"Error in post-install: {e}")
        print("If needed, you can manually download the data with:")
        print(f"  - python -m nltk.downloader -d {os.path.join(MISC_DIR, 'nltk_data')} punkt stopwords wordnet")
        print(f"  - python -m spacy download --user en_core_web_sm")

# Cleanup build files from main directory
if "install" in sys.argv:
    print("Cleaning up build artifacts from main directory...")
    cleanup_artifacts() 