import sys
import traceback
from PyQt6.QtWidgets import QApplication

# Provide alias to match requested UI import structure
from ui.main_window import JarvisWindow as MainWindow

def main():
    try:
        print("Booting JARVIS Core Systems...")
        app = QApplication(sys.argv)
        
        print("Starting UI initialization...")
        window = MainWindow()
        window.show()
        print("UI started")
        
        # Run the Qt Event Loop on the main thread
        # Note: The backend logic (listening, thinking) runs safely in the background 
        # via the VoiceWorker QThread defined inside ui/main_window.py
        sys.exit(app.exec())

    except Exception as e:
        print("Failed to start UI. See traceback below:")
        traceback.print_exc()

if __name__ == "__main__":
    main()