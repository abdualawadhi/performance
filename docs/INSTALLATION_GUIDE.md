# Installation Guide for Comprehensive Reporting

## Overview

The enhanced comprehensive reporting system requires additional dependencies beyond the base LowCode Performance Scanner. This guide will help you install and configure all necessary components.

## Core Dependencies

### Required Dependencies

```bash
# Core visualization libraries
pip install plotly>=5.0.0
pip install openpyxl>=3.0.0

# Enhanced data processing
pip install pandas>=1.3.0
pip install numpy>=1.20.0

# Report generation
pip install weasyprint>=57.0  # Optional: for PDF generation
pip install jinja2>=3.0.0     # For template rendering

# Async support
pip install aiofiles>=0.7.0  # For async file operations
```

### Optional Dependencies

```bash
# Enhanced charting (alternative to plotly)
pip install bokeh>=2.4.0

# PDF generation alternatives
pip install reportlab>=3.6.0  # Alternative PDF generator
pip install xhtml2pdf>=0.2.5  # Another PDF option

# Advanced Excel features
pip install xlsxwriter>=3.0.0  # Enhanced Excel writing
pip install pyarrow>=5.0.0     # For large data processing
```

## Installation Options

### Option 1: Install All Dependencies

```bash
# Install all comprehensive reporting dependencies
pip install -r requirements-comprehensive.txt
```

Create `requirements-comprehensive.txt`:
```txt
# Core visualization
plotly>=5.0.0
openpyxl>=3.0.0
pandas>=1.3.0
numpy>=1.20.0

# Report generation
weasyprint>=57.0
jinja2>=3.0.0

# Async support
aiofiles>=0.7.0

# Optional enhancements
bokeh>=2.4.0
reportlab>=3.6.0
xlsxwriter>=3.0.0
pyarrow>=5.0.0
```

### Option 2: Minimal Installation

```bash
# Install only essential dependencies
pip install plotly openpyxl pandas numpy aiofiles
```

### Option 3: Development Installation

```bash
# Install with development dependencies
pip install -e .
pip install plotly>=5.0.0 openpyxl>=3.0.0 pandas>=1.3.0
pip install pytest>=6.0.0 pytest-asyncio>=0.15.0  # For testing
pip install black>=22.0.0 flake8>=4.0.0           # For code quality
```

## Environment Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv_comprehensive

# Activate virtual environment
# On Windows:
venv_comprehensive\Scripts\activate
# On macOS/Linux:
source venv_comprehensive/bin/activate

# Install comprehensive reporting
pip install -r requirements-comprehensive.txt
```

### Conda Environment

```bash
# Create conda environment
conda create -n comprehensive_reporting python=3.9

# Activate environment
conda activate comprehensive_reporting

# Install dependencies
conda install -c conda-forge plotly openpyxl pandas numpy
pip install weasyprint jinja2 aiofiles
```

## Configuration

### Plotly Configuration

The system will automatically use Plotly for advanced charts if available, falling back to Chart.js if not.

```python
# Optional: Configure Plotly settings
import plotly.io as pio
pio.templates.default = "plotly_white"
pio.renderers.default = "browser"
```

### OpenPyXL Configuration

No additional configuration needed. The system will automatically use openpyxl for Excel file generation.

### Environment Variables

```bash
# Optional: Set environment variables for enhanced features
export COMPREHENSIVE_REPORTING_DEBUG=1
export COMPREHENSIVE_REPORTING_CACHE_DIR=/tmp/reports
export COMPREHENSIVE_REPORTING_TEMPLATE_DIR=/custom/templates
```

## Testing Installation

### Quick Test

```python
# Test basic functionality
python -c "
from lowcode_scanner.reporting import EnhancedReportingEngine
engine = EnhancedReportingEngine()
print('✅ Enhanced reporting system installed successfully!')
"

# Test visualization capabilities
python -c "
import plotly.graph_objects as go
fig = go.Figure()
fig.add_trace(go.Bar(x=['Test'], y=[100]))
print('✅ Plotly working correctly!')
"

# Test Excel generation
python -c "
from openpyxl import Workbook
wb = Workbook()
print('✅ OpenPyXL working correctly!')
"
```

### Full Test Suite

```bash
# Run comprehensive reporting tests
python -m pytest tests/test_comprehensive_reporting.py -v

# Run demo script
python demo_comprehensive_reporting.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # If plotly not found
   pip install plotly --upgrade
   
   # If openpyxl not found
   pip install openpyxl --upgrade
   ```

2. **Permission Errors**
   ```bash
   # Fix permissions on Linux/macOS
   chmod +x enhanced_cli.py
   
   # On Windows, run as administrator if needed
   ```

3. **Memory Issues with Large Reports**
   ```python
   # Reduce memory usage
   from lowcode_scanner.reporting import ExportSettings
   
   settings = ExportSettings(
       include_raw_data=False,  # Exclude raw data
       formats=["html", "json"]  # Limit formats
   )
   ```

4. **PDF Generation Issues**
   ```bash
   # Install WeasyPrint dependencies
   # On Ubuntu/Debian:
   sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
   
   # Alternative: Use HTML to PDF conversion
   pip install pdfkit
   ```

### Performance Optimization

1. **Large Datasets**
   ```python
   # Use chunked processing for large datasets
   from lowcode_scanner.reporting import VisualizationConfig
   
   config = VisualizationConfig(
       animations_enabled=False,  # Disable animations
       interactive_charts=False,  # Disable interactivity
       responsive_design=False   # Disable responsive features
   )
   ```

2. **Memory Management**
   ```python
   # Process reports in batches
   import asyncio
   from lowcode_scanner.reporting import generate_comprehensive_report
   
   async def process_batch(urls):
       for url in urls:
           await generate_comprehensive_report(...)
           await asyncio.sleep(0.1)  # Allow garbage collection
   ```

## Platform-Specific Notes

### Windows

```bash
# Install Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Install dependencies
pip install plotly openpyxl pandas numpy
```

### macOS

```bash
# Install Xcode command line tools
xcode-select --install

# Install dependencies
pip3 install plotly openpyxl pandas numpy

# For WeasyPrint on macOS
brew install pango gdk-pixbuf libffi
```

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv

# Install Python dependencies
pip3 install plotly openpyxl pandas numpy

# For PDF generation
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
pip3 install weasyprint
```

## Docker Support

### Dockerfile

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-comprehensive.txt .
RUN pip install -r requirements-comprehensive.txt

# Copy application
COPY . /app
WORKDIR /app

# Run the application
CMD ["python", "enhanced_cli.py", "--help"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  comprehensive-reporter:
    build: .
    volumes:
      - ./reports:/app/reports
      - ./config:/app/config
    environment:
      - COMPREHENSIVE_REPORTING_CACHE_DIR=/app/reports/cache
```

## Usage After Installation

### Basic Usage

```bash
# Test the enhanced CLI
python enhanced_cli.py --help

# Generate a comprehensive report
python enhanced_cli.py comprehensive-scan \
    --url "https://example.com" \
    --output-dir "test_reports" \
    --template professional
```

### Python API

```python
from lowcode_scanner.reporting import generate_comprehensive_report

# Generate comprehensive report
files = generate_comprehensive_report(
    result=scan_result,
    url="https://example.com",
    session_name="test",
    output_dir="reports"
)

print(f"Generated {len(files)} files")
for format_type, path in files.items():
    print(f"  {format_type}: {path}")
```

## Support

If you encounter issues during installation:

1. Check the Python version (3.8+ required)
2. Verify all dependencies are installed correctly
3. Test with the quick test commands above
4. Check the troubleshooting section
5. Refer to the main README for additional examples

For additional help, please refer to the project documentation or create an issue in the project repository.