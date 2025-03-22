#!/bin/bash

# Exit on error
set -e

# Define the output zip file
ZIP_NAME="quiz-lambda.zip"
VENV_DIR="venv"

# Remove old zip if it exists
rm -f $ZIP_NAME

# Ensure virtual environment is set up
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Navigate to the site-packages directory
cd $VENV_DIR/lib/python3.*/site-packages
zip -r ../../../../${ZIP_NAME} .

# Return to project root
cd ../../../../

# Add Python scripts to the zip
echo "Adding Python files..."
zip ${ZIP_NAME} *.py

# Add images directory (if exists)
if [ -d "images" ]; then
    echo "Adding images directory..."
    zip -r ${ZIP_NAME} images/
fi

# Deactivate the virtual environment
deactivate

echo "Packaging complete: $ZIP_NAME"
