import os
import platform

class WindowControl:
    """
    Handles OS-specific window management commands.
    """
    def __init__(self):
        self.system = platform.system()

    def minimize(self):
        """Minimize the currently active window."""
        try:
            if self.system == "Darwin":
                # Mac: Minimize frontmost window
                cmd = "osascript -e 'tell application \"System Events\" to set miniaturized of window 1 of (first process whose frontmost is true) to true'"
                os.system(cmd)
            elif self.system == "Windows":
                # Windows: Minimize all (closest standard command without ctypes)
                os.system('powershell -command "(New-Object -ComObject Shell.Application).MinimizeAll()"')
            return True
        except Exception as e:
            print(f"Window minimize error: {e}")
            return False

    def maximize(self):
        """Maximize the currently active window."""
        try:
            if self.system == "Darwin":
                # Mac: Zoom (maximize) frontmost window
                cmd = "osascript -e 'tell application \"System Events\" to set zoomed of window 1 of (first process whose frontmost is true) to true'"
                os.system(cmd)
            elif self.system == "Windows":
                # Windows maximize is complex without pygetwindow, so we'll use a shortcut simulation
                os.system('powershell -command "$wshell = New-Object -ComObject WScript.Shell; $wshell.SendKeys(\'#{UP}\')"')
            return True
        except Exception as e:
            print(f"Window maximize error: {e}")
            return False

    def close_front(self):
        """Close the currently active window."""
        try:
            if self.system == "Darwin":
                # Mac: Cmd + W
                os.system("osascript -e 'tell application \"System Events\" to keystroke \"w\" using command down'")
            elif self.system == "Windows":
                # Windows: Ctrl + W
                os.system('powershell -command "$wshell = New-Object -ComObject WScript.Shell; $wshell.SendKeys(\'^{w}\')"')
            return True
        except Exception as e:
            print(f"Window close error: {e}")
            return False

    def close_folder(self, name):
        """Close a specific folder window by name."""
        try:
            import subprocess
            if self.system == "Darwin":
                script = f"""
                tell application "Finder"
                    set folder_windows to (every window whose name contains "{name}")
                    if (count of folder_windows) is 0 then
                        return "NOT_FOUND"
                    end if
                    repeat with fw in folder_windows
                        close fw
                    end repeat
                    return "SUCCESS"
                end tell
                """
                result = subprocess.check_output(["osascript", "-e", script]).decode().strip()
                return result == "SUCCESS"
            elif self.system == "Windows":
                ps_script = f"""
                $shell = New-Object -ComObject Shell.Application;
                $closed = $false
                foreach ($win in $shell.Windows()) {{
                    if ($win.LocationName -match "{name}") {{
                        $win.Quit()
                        $closed = $true
                    }}
                }}
                if ($closed) {{ Write-Output "SUCCESS" }} else {{ Write-Output "NOT_FOUND" }}
                """
                result = subprocess.check_output(["powershell", "-command", ps_script.strip()]).decode().strip()
                return "SUCCESS" in result
            return False
        except Exception as e:
            print(f"Folder close error: {e}")
            return False

    def close_application(self, name):
        """Quit a specific application."""
        try:
            import subprocess
            if self.system == "Darwin":
                script = f"""
                if application "{name}" is running then
                    tell application "{name}" to quit
                    return "SUCCESS"
                else
                    return "NOT_FOUND"
                end if
                """
                result = subprocess.check_output(["osascript", "-e", script]).decode().strip()
                return result == "SUCCESS"
            elif self.system == "Windows":
                # Uses taskkill and checks if it was successful (code 0 is success, 128 is not found usually)
                status = os.system(f'taskkill /f /fi "WINDOWTITLE eq *{name}*"')
                return status == 0
            return False
        except Exception as e:
            print(f"App close error: {e}")
            return False

    def close_last(self, last_entity):
        """Fallback to close whatever the last opened entity was."""
        if not last_entity:
            return self.close_front()
            
        # Extract the basic name without the path
        name = os.path.basename(os.path.normpath(last_entity))
        
        # Determine if it's a folder or file/app based on existence
        if os.path.isdir(last_entity):
            return self.close_folder(name)
        else:
            return self.close_application(name)

# Singleton instance
window_manager = WindowControl()
