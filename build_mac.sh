#!/bin/bash

echo "🚀 Starting macOS Build for Jarvis..."

# Ensure pyinstaller is installed
pip install pyinstaller

# Clean old builds
rm -rf build dist

# Build the application
# --windowed: Creates a .app bundle without a console window
# --name: The name of the final application
# --add-data: Includes necessary data files
pyinstaller \
    --windowed \
    --name "Jarvis" \
    --add-data "data/file_index.json:data" \
    --add-data "data/automations.json:data" \
    main.py

echo "✅ Build Complete! App is located in the dist/ folder."
echo "⚠️  Note: When you run Jarvis.app for the first time, macOS will ask for Microphone and Accessibility permissions."
