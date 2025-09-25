#!/usr/bin/env python3
"""
Setup script for Dental Practice AI Toolkit
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("config/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dental-practice-ai-toolkit",
    version="1.0.0",
    author="LangChain AI Solutions",
    author_email="dental@langchain-ai.com",
    description="Complete AI-powered practice management solution for dental practices",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/langchain-ai/dental-practice-toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Healthcare Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Healthcare",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "production": [
            "gunicorn>=21.2.0",
            "nginx>=1.0.0",
            "supervisor>=4.2.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "dental-ai=dental_suite:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml", "*.json"],
    },
    keywords=[
        "dental",
        "healthcare",
        "ai",
        "practice management",
        "langchain",
        "automation",
        "ireland",
        "gdpr",
        "insurance",
        "patient management"
    ],
    project_urls={
        "Bug Reports": "https://github.com/langchain-ai/dental-practice-toolkit/issues",
        "Documentation": "https://docs.langchain-dental.ie",
        "Source": "https://github.com/langchain-ai/dental-practice-toolkit",
        "Demo": "https://demo.langchain-dental.ie",
        "Support": "https://support.langchain-dental.ie",
    },
    license="MIT",
    platforms=["any"],
    zip_safe=False,
)