#!/bin/bash

# Exit on error
set -e

# Define the output zip file
ZIP_NAME="quiz-lambda.zip"

cd env/lib/python3.12/site-packages
zip -r ../../../../${ZIP_NAME} .

# Copy Python files
echo "Copying Python files..."
cd ../../../../
zip ${ZIP_NAME} *.py

# Copy images directory
echo "Copying images directory..."
zip ${ZIP_NAME} images/*

echo "Packaging complete: $ZIP_NAME"
