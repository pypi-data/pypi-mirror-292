from setuptools import setup, find_packages

# Read the contents of README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FileMa",  # Replace with your own library name
    version="0.1.5",
    author="Ahmed ZOUITANE",
    author_email="zouitane.ahmed02@gmail.com",
    description="The `FileMa` (File Management)  library provides utilities for file and directory management in Python. It includes functions for creating, removing, renaming, copying files and directories, as well as reading file contents, printing directory structures, and more. The library uses colored terminal output for better visual feedback.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZOUITANE-Ahmed/FileMa.git",  # Replace with the URL of your GitHub repo
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "colorama>=0.4.4",
    ],
)
