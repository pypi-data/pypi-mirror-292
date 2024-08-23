# File: setup.py
from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="demingfit",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
    ],
    author="Dalawey Chen",    
    description="A package for performing Deming regression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dalawey/deming_regression.git",
    project_urls={
        "Bug Tracker": "https://github.com/dalawey/deming_regression/issues",
        "Documentation": "https://github.com/dalawey/deming_regression/wiki",
        "Source Code": "https://github.com/dalawey/deming_regression",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    python_requires=">=3.7",
    keywords="deming regression statistics data-analysis",
)

# The rest of the package structure remains the same as in the previous artifact