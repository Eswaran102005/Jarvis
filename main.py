import sys
import os

# Add the project root to sys.path to resolve core/feature imports dynamically
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import JarvisWindow

def main():
    print("Booting JARVIS Core Systems...")
    app = QApplication(sys.argv)
    
    # Initialize the main UI
    window = JarvisWindow()
    window.show()
    
    # Run the Qt Event Loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
