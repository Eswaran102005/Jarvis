import os
import json
import platform
import time
from core.paths import FILE_INDEX_PATH

INDEX_FILE = FILE_INDEX_PATH

# Strict ignore list to avoid heavy/system folders
IGNORE_FOLDERS = {
    "Library", "System", "Applications", "node_modules", ".git", 
    "AppData", "Windows", "Program Files", "Program Files (x86)",
    ".gemini", ".vscode", "__pycache__", ".cache", "venv", "env",
    "bin", "boot", "dev", "etc", "lib", "lib64", "sbin", "tmp", "var"
}

def build_index():
    system = platform.system()
    
    # Root paths to scan
    if system == "Windows":
        search_paths = ["C:\\Users"] # Safer than full C:\, but can be changed to ["C:\\"] if requested
    else:
        search_paths = ["/Users"]

    data = []
    print(f"Indexing started on {search_paths}...")
    start_time = time.time()

    for root_path in search_paths:
        if not os.path.exists(root_path): continue
        
        for root, dirs, files in os.walk(root_path):
            # Prune directories in-place to stay fast
            dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS and not d.startswith('.')]
            
            try:
                # 📂 Index Folders
                for folder in dirs:
                    folder_path = os.path.join(root, folder)
                    data.append({
                        "name": folder.lower(),
                        "path": folder_path,
                        "type": "folder",
                        "mtime": os.path.getmtime(folder_path),
                        "usage_score": 0
                    })

                # 📄 Index Files
                for file in files:
                    if file.startswith('.'): continue
                    file_path = os.path.join(root, file)
                    data.append({
                        "name": file.lower(),
                        "path": file_path,
                        "type": "file",
                        "mtime": os.path.getmtime(file_path),
                        "usage_score": 0
                    })
            except (PermissionError, OSError):
                continue

    try:
        with open(INDEX_FILE, "w") as f:
            json.dump(data, f, indent=2)
        
        duration = time.time() - start_time
        print(f"Indexing completed in {duration:.2f}s! Indexed {len(data)} items.")
    except Exception as e:
        print(f"Error saving index: {e}")

if __name__ == "__main__":
    build_index()