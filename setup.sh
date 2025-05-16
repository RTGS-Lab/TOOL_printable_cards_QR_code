#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activation instructions
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate  # On macOS/Linux"
echo "  venv\\Scripts\\activate     # On Windows"
echo ""

# Install dependencies
echo "After activating, install dependencies with:"
echo "  pip install -r requirements.txt"
echo ""

echo "Setup complete!"