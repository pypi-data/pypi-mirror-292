from setuptools import setup, find_packages
import os

# Read the contents of your README file
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="old-doc",
    version="0.0.3",
    description="Easily create synthetic data for HTR and OCR",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="WJB Mattingly",
    url="https://github.com/wjbmattingly/old-doc",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "Pillow",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.8',
)