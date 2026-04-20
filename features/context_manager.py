import json
import os

class ContextManager:
    """
    Manages session context, entity resolution, and safety confirmations.
    """
    def __init__(self):
        self.last_entity = None  # Stores the last file/folder path used
        self.last_action = None  # Stores the last intent executed
        self.history = []        # Stack of recent entities for deeper context
        self.pending_confirmation = None # Stores an action that needs "Are you sure?"

    def update(self, action, entity):
        """Update context with new data."""
        self.last_action = action
        if entity:
            self.last_entity = entity
            self.history.append(entity)
            if len(self.history) > 10:
                self.history.pop(0)

    def resolve(self, target):
        """
        Resolves pronouns like 'it', 'that', 'this' to the last entity.
        Returns the resolved target string.
        """
        pronouns = ["it", "that", "this", "there", "the file", "the folder"]
        if target.lower() in pronouns:
            return self.last_entity if self.last_entity else target
        
        # Handle cases like "rename it to final"
        if " it " in f" {target.lower()} ":
            if self.last_entity:
                # Get the filename from the path to stay within the command context
                name = os.path.basename(self.last_entity)
                return target.lower().replace("it", name).strip()
        
        return target

    def set_pending(self, action_func, message):
        """Set an action as pending user confirmation."""
        self.pending_confirmation = {"func": action_func, "msg": message}

    def clear_pending(self):
        """Clear any pending actions."""
        self.pending_confirmation = None

# Singleton instance
context = ContextManager()
