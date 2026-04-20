@echo off
echo 🚀 Starting Windows Build for Jarvis...

:: Ensure pyinstaller is installed
pip install pyinstaller

:: Clean old builds
rmdir /s /q build
rmdir /s /q dist

:: Build the application
:: --onefile: Bundles everything into a single .exe
:: --windowed: Hides the console window
:: --name: The name of the final application
:: --add-data: Includes necessary data files (format differs slightly from Mac: uses semicolon)
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Jarvis" ^
    --add-data "data\file_index.json;data" ^
    --add-data "data\automations.json;data" ^
    main.py

echo ✅ Build Complete! App is located in the dist\ folder.
echo ⚠️  Note: You may need to grant Microphone permissions in Windows Settings for the Voice Assistant to work.
pause
