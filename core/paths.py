import os
import sys

def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not bundled, use the project root (one level up from core/)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)

# Data Paths
FILE_INDEX_PATH = get_resource_path(os.path.join("data", "file_index.json"))
AUTOMATIONS_PATH = get_resource_path(os.path.join("data", "automations.json"))
ASSETS_DIR = get_resource_path("assets")
