import sys
import os

# Add root just in case
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from features.window_control import window_manager
window_manager.close_folder("downloads")
