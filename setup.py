#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read README.md for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove version constraints for flexibility
                package = line.split('>=')[0].split('==')[0].split('<')[0]
                requirements.append(package)

setup(
    name="optics-toolbox",
    version="1.0.0",
    author="Michael Akridge",
    author_email="michael.akridge@noaa.gov",
    description="User-friendly Google Cloud Storage bucket browser and downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelAkridge-NOAA/optics-toolbox",
    project_urls={
        "Bug Tracker": "https://github.com/MichaelAkridge-NOAA/optics-toolbox/issues",
        "Documentation": "https://github.com/MichaelAkridge-NOAA/optics-toolbox",
        "Source Code": "https://github.com/MichaelAkridge-NOAA/optics-toolbox",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Filesystems",
        "Topic :: Internet :: File Transfer Protocol (FTP)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "gcs-browser=gcs_browser.cli:main",
            "gcs-browser-web=gcs_browser.web:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gcs_browser": ["*.json", "*.md"],
    },
    keywords=[
        "google-cloud-storage",
        "gcs",
        "cloud-storage", 
        "file-browser",
        "downloader",
        "sync",
        "gsutil",
        "noaa",
        "data-management",
    ],
    zip_safe=False,
)
