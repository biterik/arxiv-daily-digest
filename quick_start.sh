#!/bin/bash
# Quick Start Script for arXiv Daily Digest
# Copyright (c) 2025 Erik Bitzek
# Licensed under GNU AGPL v3

set -e  # Exit on error

echo "=========================================="
echo "arXiv Daily Digest - Quick Start"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Check for conda
if command -v conda &> /dev/null; then
    echo "✓ Found Conda"
    USE_CONDA=true
else
    echo "ℹ Conda not found, will use venv"
    USE_CONDA=false
fi

# Create environment
echo
echo "Setting up environment..."

if [ "$USE_CONDA" = true ]; then
    conda env create -f environment.yml
    echo
    echo "✓ Conda environment created"
    echo
    echo "To activate:"
    echo "  conda activate arxiv-digest"
else
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo
    echo "✓ Virtual environment created"
    echo
    echo "To activate:"
    echo "  source venv/bin/activate"
fi

echo
echo "=========================================="
echo "Next steps:"
echo "=========================================="
echo
echo "1. Get OpenAI API key from: https://platform.openai.com/"
echo
echo "2. Set your API key:"
echo "   export OPENAI_API_KEY='sk-your-key-here'"
echo
echo "3. Edit config.yml with your keywords"
echo
echo "4. Run the digest:"
if [ "$USE_CONDA" = true ]; then
    echo "   conda activate arxiv-digest"
else
    echo "   source venv/bin/activate"
fi
echo "   cd src"
echo "   python main.py"
echo
echo "5. Check the output: daily_digest.txt"
echo
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="