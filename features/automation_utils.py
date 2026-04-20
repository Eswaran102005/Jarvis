import pyautogui
import pyperclip
import time
import platform

class AutomationUtils:
    """
    Handles robust GUI automation like typing and saving.
    """
    def __init__(self):
        self.system = platform.system()
        # Fail-safe: move mouse to corner to abort
        pyautogui.FAILSAFE = True

    def type_smart(self, text, delay=1.5):
        """
        Pastes text into the current focused window.
        - copies text to clipboard
        - waits for focus delay
        - triggers Cmd+V (Mac) or Ctrl+V (Windows)
        """
        if not text:
            return False
            
        try:
            # 1. Store original clipboard to restore later (optional but nice)
            # original_clipboard = pyperclip.paste()
            
            # 2. Copy target text
            pyperclip.copy(text)
            
            # 3. Wait for app to gain focus (crucial for "open and write")
            time.sleep(delay)
            
            # 4. Paste
            if self.system == "Darwin":
                pyautogui.hotkey('command', 'v')
            else:
                pyautogui.hotkey('ctrl', 'v')
                
            return True
        except Exception as e:
            print(f"Typing error: {e}")
            return False

    def save_current(self):
        """Triggers the OS-standard Save shortcut."""
        try:
            if self.system == "Darwin":
                pyautogui.hotkey('command', 's')
            else:
                pyautogui.hotkey('ctrl', 's')
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

# Singleton instance
automation_tools = AutomationUtils()
