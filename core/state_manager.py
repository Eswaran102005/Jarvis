import time
import os
import sys
import json
import logging
from pathlib import Path
from threading import Event

# Global exit signal
stop_event = Event()

# 🛠️ Path Resolution Helper
def get_base_path():
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(os.path.abspath(".")).resolve()

def get_writable_dir(app_name="Jarvis", sub_dir="Data"):
    """Get or create a writable directory in the user's home (macOS standard)."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / ("Logs" if sub_dir == "Logs" else "Application Support") / app_name
    else:
        base = Path.home() / f".{app_name.lower()}" / sub_dir
    
    base.mkdir(parents=True, exist_ok=True)
    return base

# 📝 Centralized Logging Setup
LOG_DIR = get_writable_dir(sub_dir="Logs")
LOG_FILE = LOG_DIR / "jarvis.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("JarvisCore")

class StateManager:
    """
    Central shared state with built-in logging and config validation.
    """
    def __init__(self):
        self.state = {
            "status": "idle",
            "user_text": "",
            "assistant_text": "",
            "search_results": [],
            "last_update": time.time(),
            "errors": []
        }
        logger.info(f"StateManager initialized. Logs located at: {LOG_FILE}")

    def set(self, key, value):
        self.state[key] = value
        self.state["last_update"] = time.time()
        if key == "status":
            logger.info(f"System Status -> {value}")

    def log_error(self, message):
        """Record and log system errors."""
        logger.error(message)
        self.state["errors"].append({
            "ts": time.time(),
            "msg": message
        })

    def get_all(self):
        return self.state

    def clear_results(self):
        self.state["search_results"] = []
        self.state["last_update"] = time.time()

    def load_json_safe(self, filename, default_content):
        """
        Production-ready JSON loader with auto-repair and bundle awareness.
        """
        # 1. Determine paths
        # Writable path (User's Application Support)
        data_dir = get_writable_dir(sub_dir="Data")
        writable_path = data_dir / filename
        
        # Bundled path (Static default from PyInstaller bundle)
        bundled_path = get_base_path() / "data" / filename

        try:
            # If writable file doesn't exist, try to copy/seed from bundled version
            if not writable_path.exists():
                logger.warning(f"Config {filename} missing in Application Support. Seeding...")
                
                source_data = default_content
                if bundled_path.exists():
                    with open(bundled_path, 'r') as f:
                        source_data = json.load(f)
                
                with open(writable_path, 'w') as f:
                    json.dump(source_data, f, indent=4)
                return source_data

            # Standard load from writable path
            with open(writable_path, 'r') as f:
                return json.load(f)
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load {filename}: {e}. Repairing with defaults.")
            # Backup corrupted file
            if writable_path.exists():
                os.rename(str(writable_path), f"{writable_path}.bak")
            
            with open(writable_path, 'w') as f:
                json.dump(default_content, f, indent=4)
            return default_content

# Singleton
shared_state = StateManager()
