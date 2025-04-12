#!/bin/bash
set -e

# Create and activate environment
echo "Creating and activating mamba environment..."
mamba create -n finbuddy-ai python=3.11 -y
source $(conda info --base)/etc/profile.d/conda.sh
conda activate finbuddy-ai

# Install frontend
echo "Installing frontend dependencies..."
cd finbuddy-ai
npm install

# Install backend
echo "Installing backend dependencies..."
cd backend
mamba install --file requirements.txt -y

echo "✅ Environment setup complete!"
