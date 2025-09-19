"""
Setup script for LangChain Small Business Agents

This package provides a comprehensive suite of AI-powered agents designed
to automate and enhance various aspects of small business operations.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as f:
        requirements = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and "# Built-in Python module" not in line
        ]
else:
    requirements = []

# Read version from src/__init__.py
version = "1.0.0"
init_path = Path(__file__).parent / "src" / "__init__.py"
if init_path.exists():
    with open(init_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setup(
    name="langchain-small-business-agents",
    version=version,
    author="LangChain Small Business Team",
    author_email="support@langchain-business.com",
    description="AI-powered business automation agents using LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/langchain-small-business-agents",
    project_urls={
        "Bug Reports": "https://github.com/your-org/langchain-small-business-agents/issues",
        "Source": "https://github.com/your-org/langchain-small-business-agents",
        "Documentation": "https://langchain-small-business-agents.readthedocs.io/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.2",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "performance": [
            "cython>=3.0.7",
            "numba>=0.58.1",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "loguru>=0.7.2",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "azure-storage-blob>=12.19.0",
            "google-cloud-storage>=2.10.0",
        ],
        "full": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.2",
            "pytest-mock>=3.12.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
            "cython>=3.0.7",
            "numba>=0.58.1",
            "prometheus-client>=0.19.0",
            "loguru>=0.7.2",
            "boto3>=1.34.0",
            "azure-storage-blob>=12.19.0",
            "google-cloud-storage>=2.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "langchain-agents=src.cli:main",
            "lc-agents=src.cli:main",
            "business-agents=src.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.txt",
            "*.md",
            "templates/*",
            "data/*",
        ],
    },
    zip_safe=False,
    keywords=[
        "langchain",
        "ai agents",
        "business automation",
        "customer service",
        "sales",
        "marketing",
        "financial analysis",
        "hr",
        "inventory management",
        "document processing",
        "social media",
        "email marketing",
        "market research",
        "small business",
        "artificial intelligence",
        "machine learning",
        "nlp",
        "automation",
    ],
    platforms=["any"],
    license="MIT",
    test_suite="tests",
    tests_require=[
        "pytest>=7.4.4",
        "pytest-asyncio>=0.23.2",
        "pytest-mock>=3.12.0",
        "pytest-cov>=4.1.0",
    ],
)