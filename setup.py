#!/usr/bin/env python3
"""
Setup script for Professional Low-Code Performance Scanner.

This package provides comprehensive performance testing specifically designed
for low-code web applications including Bubble.io, OutSystems, and Airtable.
"""

import pathlib

from setuptools import find_packages, setup

# Read the contents of README files
current_dir = pathlib.Path(__file__).parent
readme_path = current_dir / "README_PROFESSIONAL.md"

if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")
else:
    long_description = (current_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="lowcode-performance-scanner",
    version="1.0.2",
    author="Professional Performance Scanner Team",
    author_email="support@lowcode-scanner.com",
    description="Professional performance testing for low-code web applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/lowcode-performance-scanner",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core Dependencies
        "pydantic>=2.0.0",
        "playwright>=1.40.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "asyncio-throttle>=1.0.2",
        # Data Processing
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        # Image Processing
        "Pillow>=10.0.0",
        # HTTP Clients
        "httpx>=0.25.0",
        "aiohttp>=3.9.0",
        "aiofiles>=23.0.0",
        # CLI and UI
        "click>=8.1.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        # Report Generation
        "jinja2>=3.1.0",
        "openpyxl>=3.1.0",
        "reportlab>=4.0.0",
        "plotly>=5.17.0",
        "matplotlib>=3.7.0",
        # System Information
        "psutil>=5.9.0",
        # Logging
        "structlog>=23.0.0",
        # Configuration
        "jsonschema>=4.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "isort>=5.12.0",
            "pre-commit>=3.4.0",
            "coverage>=7.3.0",
            "bandit>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
        "advanced": [
            # Advanced analytics
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "scikit-learn>=1.3.0",
            "seaborn>=0.12.0",
            "bokeh>=3.3.0",
            # Performance profiling
            "memory-profiler>=0.61.0",
            "py-spy>=0.3.14",
            # Cloud storage
            "boto3>=1.29.0",
            "google-cloud-storage>=2.10.0",
            # Database support
            "sqlalchemy>=2.0.0",
        ],
        "enterprise": [
            # Enterprise features
            "redis>=5.0.0",
            "celery>=5.3.0",
            "prometheus-client>=0.18.0",
            "sentry-sdk>=1.38.0",
            # Security
            "cryptography>=41.0.0",
            "certifi>=2023.0.0",
            # Advanced networking
            "scapy>=2.5.0",
            "dnspython>=2.4.0",
        ],
        "pdf": [
            "weasyprint>=60.0",
        ],
        "all": [
            # Include all extras
            "jupyter>=1.0.0",
            "notebook>=7.0.0",
            "scikit-learn>=1.3.0",
            "seaborn>=0.12.0",
            "bokeh>=3.3.0",
            "memory-profiler>=0.61.0",
            "py-spy>=0.3.14",
            "boto3>=1.29.0",
            "google-cloud-storage>=2.10.0",
            "sqlalchemy>=2.0.0",
            "redis>=5.0.0",
            "celery>=5.3.0",
            "prometheus-client>=0.18.0",
            "sentry-sdk>=1.38.0",
            "cryptography>=41.0.0",
            "certifi>=2023.0.0",
            "scapy>=2.5.0",
            "dnspython>=2.4.0",
            "weasyprint>=60.0",
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "lowcode-scanner=lowcode_scanner.__main__:main",
            "lcs=lowcode_scanner.__main__:main",
            "performance-scanner=lowcode_scanner.__main__:main",
        ],
    },
    package_data={
        "lowcode_scanner": [
            "reporting/templates/*.html",
            "reporting/templates/*.jinja2",
            "reporting/templates/*.css",
            "reporting/templates/*.js",
            "browser/scripts/*.js",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    include_package_data=True,
    keywords=[
        # Core keywords
        "performance-testing",
        "web-performance",
        "low-code",
        "no-code",
        # Platform keywords
        "bubble",
        "outsystems",
        "airtable",
        "mendix",
        "powerapps",
        # Technical keywords
        "playwright",
        "browser-automation",
        "core-web-vitals",
        "memory-profiling",
        "performance-monitoring",
        "lighthouse",
        "pagespeed",
        # Use case keywords
        "qa-testing",
        "performance-audit",
        "web-optimization",
        "site-speed",
        "user-experience",
        "professional-reporting",
    ],
    project_urls={
        "Homepage": "https://lowcode-performance-scanner.com",
        "Documentation": "https://docs.lowcode-performance-scanner.com",
        "Repository": "https://github.com/your-org/lowcode-performance-scanner",
        "Bug Tracker": "https://github.com/your-org/lowcode-performance-scanner/issues",
        "Changelog": "https://github.com/your-org/lowcode-performance-scanner/blob/main/CHANGELOG.md",
        "Discussions": "https://github.com/your-org/lowcode-performance-scanner/discussions",
    },
    zip_safe=False,  # Required for proper template loading
    platforms=["any"],
    license="MIT",
    license_files=["LICENSE"],
)
