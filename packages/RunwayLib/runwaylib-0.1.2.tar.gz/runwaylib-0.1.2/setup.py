# setup.py

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="runwaylib",
    version="0.1.2",
    author="Parsa",
    author_email="your.email@example.com",  # Add your email here
    description="A lib for a server",  # Update this with a brief description of your library
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/runway",  # Add your project's homepage URL here
    py_modules=["runway"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Specify the license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],  # Add dependencies here if your package has any
)
