#!/bin/bash
# One-click automated setup script for JarvisLabs GPU instance
set -e

echo "=================================================="
echo "    STARTING MANHWA RECAP SETUP ON JARVISLABS     "
echo "=================================================="

# Update system & install FFmpeg
echo "[1/4] Installing FFmpeg and system dependencies..."
sudo apt-get update -y && sudo apt-get install -y ffmpeg git wget curl python3-pip python3-venv

# Install Python packages
echo "[2/4] Installing Python requirements..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Pre-download models
echo "[3/4] Downloading AI Model Weights..."
python3 scripts/download_models.py

echo "=================================================="
echo "    SETUP COMPLETE! READY TO RUN RECAP ENGINE    "
echo "=================================================="
echo "To run CLI demo:"
echo "   python3 cli.py process --chapter-name solo_leveling --voice af_heart"
echo ""
echo "To run Streamlit Web UI:"
echo "   streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
echo "=================================================="
