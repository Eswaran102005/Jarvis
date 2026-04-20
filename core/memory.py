import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    """Load user memory from storage."""
    try:
        if not os.path.exists(MEMORY_FILE):
            return {}
        
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading memory: {e}")
        return {}

def save_memory(data):
    """Save user memory to persistent storage."""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving memory: {e}")

def remember(key, value):
    """Store a key-value pair in memory."""
    data = load_memory()
    data[key.lower().strip()] = value.strip()
    save_memory(data)

def recall(key):
    """Retrieve a value from memory by its key."""
    data = load_memory()
    return data.get(key.lower().strip(), None)