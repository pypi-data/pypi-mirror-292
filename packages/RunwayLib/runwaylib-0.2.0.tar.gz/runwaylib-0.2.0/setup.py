# setup.py
from setuptools import setup, find_packages
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="runwaylib",  # Name should be in lowercase
    version="0.2.0",
    description="A library for a server",
    author="Parsa",
    author_email="your-email@example.com",
    packages=find_packages(),  # Automatically find the runwaylib package
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
