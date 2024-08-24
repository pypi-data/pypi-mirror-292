# setup.py
from setuptools import setup, find_packages
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="RunwayLib",  # Name as seen on PyPI
    version="0.4.1",  # Increment this version for updates
    description="A library for a server",
    author="Parsa",
    author_email="your-email@example.com",  # Optional
    packages=find_packages(),  # Automatically find the RunwayLib packag
    install_requires=[],  # List any dependencies here
    classifiers=[  # Optional, to specify the package's audience
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify minimum Python version
)
