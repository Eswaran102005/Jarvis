import os
import json

from core.paths import AUTOMATIONS_PATH

class AutomationManager:
    """
    Manages automated command groups and user habit mappings.
    """
    def __init__(self):
        self.automations = {
            "start working": ["open chrome", "open notepad", "open projects folder"],
            "shut down everything": ["close chrome", "close notepad", "close window"],
            "morning routine": ["open google", "get time"],
            "clean workspace": ["close window"]
        }
        self.config_path = AUTOMATIONS_PATH
        self.load_config()

    def load_config(self):
        """Load user-defined automations from JSON."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    self.automations.update(json.load(f))
            except Exception as e:
                print(f"Error loading automations: {e}")

    def get_actions(self, command):
        """Returns a list of commands for a given automation trigger."""
        cmd = command.lower().strip()
        for trigger, actions in self.automations.items():
            if trigger in cmd:
                return actions
        return None

# Singleton instance
automation = AutomationManager()
