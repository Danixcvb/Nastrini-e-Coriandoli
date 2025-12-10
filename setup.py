"""
Setup script per Tool Nastri Leonardo
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tool-nastri-leonardo",
    version="1.0.0",
    author="Leonardo Team",
    description="Tool per la generazione automatica di file di configurazione SCL/DB per sistemi di nastri trasportatori",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(exclude=["tests", "tools", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "nastri-tool=main:main",
        ],
    },
)

