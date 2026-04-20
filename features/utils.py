import os
import platform
import subprocess
import webbrowser

os_name = platform.system()

def open_notepad():
    """Open the system default text editor."""
    try:
        if os_name == "Windows":
            subprocess.Popen(["notepad.exe"])
        elif os_name == "Darwin":
            subprocess.Popen(["open", "-a", "TextEdit"])
        else:
            print("Unsupported OS")
    except Exception as e:
        print(f"Error opening editor: {e}")

def open_chrome():
    """Open Google Chrome."""
    try:
        if os_name == "Windows":
            subprocess.Popen(["start", "chrome"], shell=True)
        elif os_name == "Darwin":
            subprocess.Popen(["open", "-a", "Google Chrome"])
        else:
            print("Unsupported OS")
    except Exception as e:
        print(f"Error opening Chrome: {e}")

def open_file(filepath):
    """Open any file or folder using the default system application."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        if os_name == "Windows":
            os.startfile(filepath)
        elif os_name == "Darwin":
            subprocess.Popen(["open", filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
    except Exception as e:
        print(f"Error opening file: {e}")

def close_app(app_name):
    """Close an application by name."""
    try:
        if os_name == "Windows":
            os.system(f"taskkill /f /im {app_name}.exe")
        elif os_name == "Darwin":
            os.system(f"pkill -f '{app_name}'")
    except Exception as e:
        print(f"Error closing app: {e}")

def open_url(url):
    """Open a URL in the default web browser."""
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"Error opening URL: {e}")

def close_window(target_type="folder"):
    """Close the active folder or window."""
    try:
        if os_name == "Darwin":
            if target_type == "folder":
                os.system("osascript -e 'tell application \"Finder\" to close front window'")
            else:
                # Generic close window (Cmd+W)
                os.system("osascript -e 'tell application \"System Events\" to keystroke \"w\" using command down'")
        elif os_name == "Windows":
            if target_type == "folder":
                # Safely close only Explorer windows
                cmd = 'powershell -command "(New-Object -ComObject Shell.Application).Windows() | Where-Object { $_.Name -eq \'File Explorer\' -or $_.Name -eq \'Windows Explorer\' } | ForEach-Object { $_.Quit() }"'
                os.system(cmd)
            else:
                # Taskkill fallback for apps is already in close_app
                pass
    except Exception as e:
        print(f"Error closing window: {e}")

def system_command(cmd_type):
    """Execute system-level commands like shutdown or sleep."""
    try:
        if cmd_type == "shutdown":
            if os_name == "Windows":
                os.system("shutdown /s /t 1")
            else:
                os.system("sudo shutdown -h now")
        elif cmd_type == "sleep":
            if os_name == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif os_name == "Darwin":
                os.system("pmset sleepnow")
    except Exception as e:
        print(f"System command error: {e}")