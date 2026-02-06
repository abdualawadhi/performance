#!/bin/bash

echo "🧹 Cleaning up project for GitHub upload..."

# Remove Node modules (largest space saver)
echo "📦 Removing Node modules..."
rm -rf frontend/node_modules

# Remove Python cache
echo "🐍 Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.pyo" -delete 2>/dev/null

# Remove virtual environments
echo "🔧 Removing virtual environments..."
rm -rf venv .venv env ENV

# Remove generated reports
echo "📊 Removing generated reports..."
rm -rf performance_reports/*.html
rm -rf performance_reports/*.json
rm -rf performance_reports/*.csv
rm -rf performance_reports/*.pdf
rm -rf performance_reports/*.xlsx

# Remove IDE files
echo "💻 Removing IDE files..."
rm -rf .vscode .idea *.swp *.swo

# Remove OS files
echo "🖥️ Removing OS files..."
find . -name ".DS_Store" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null

# Remove log files
echo "📝 Removing log files..."
find . -name "*.log" -delete 2>/dev/null

# Remove temporary files
echo "🗂️ Removing temporary files..."
find . -name "*.tmp" -delete 2>/dev/null
find . -name "*.temp" -delete 2>/dev/null

echo "✅ Cleanup complete!"
echo ""
echo "📊 Project size reduction:"
echo "   - Before: $(du -sh . 2>/dev/null | cut -f1)"
echo "   - After:  $(du -sh . 2>/dev/null | cut -f1)"
echo ""
echo "🚀 Ready for GitHub upload!"
