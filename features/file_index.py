import json
import os
import platform
import subprocess
from core.paths import FILE_INDEX_PATH

INDEX_FILE = FILE_INDEX_PATH
_cached_index = None

def load_index():
    """Load index into memory for instant search."""
    global _cached_index
    if _cached_index is None:
        try:
            if os.path.exists(INDEX_FILE):
                with open(INDEX_FILE, "r") as f:
                    _cached_index = json.load(f)
            else:
                _cached_index = []
        except Exception as e:
            print(f"Error loading index: {e}")
            _cached_index = []
    return _cached_index

import difflib

def smart_search(name, search_type=None, limit=5):
    """
    Search index with scoring: Exact > StartsWith > Fuzzy > Contains.
    Includes usage_score and recency in weighting.
    """
    data = load_index()
    query = name.lower().strip()
    if not query: return []
 
    matches = []
    for item in data:
        if search_type and item["type"] != search_type:
            continue
            
        item_name = item["name"]
        score = 0
        
        # 🟢 1. Exact Match
        if query == item_name: 
            score = 100
        # 🟡 2. Starts with Query
        elif item_name.startswith(query): 
            score = 70
        # 🟠 3. Fuzzy Similarity (Word-based)
        else:
            words = item_name.replace('_', ' ').replace('-', ' ').split('.')
            # Also split by space
            words = [w for part in words for w in part.split()]
            
            best_word_score = 0
            for word in words:
                similarity = difflib.SequenceMatcher(None, query, word).ratio()
                if similarity > 0.8: # High threshold for word match
                    best_word_score = int(similarity * 60)
                    break
            
            if best_word_score > 0:
                score = best_word_score
            # 🔵 4. Simple 'in' match fallback
            elif query in item_name:
                score = 30
        
        if score > 0:
            # 🚀 usage_score boost
            usage_boost = min(item.get("usage_score", 0) * 2, 20)
            score += usage_boost
            
            matches.append({
                "path": item["path"],
                "name": item_name,
                "score": score,
                "len": len(item_name),
                "mtime": item.get("mtime", 0),
                "type": item["type"]
            })

    # Sort: Score (desc) -> Recency (desc) -> Length (asc)
    matches.sort(key=lambda x: (-x["score"], -x["mtime"], x["len"]))
    return matches[:limit]

def increment_usage(path):
    """Boost the usage score for a frequently used path."""
    global _cached_index
    data = load_index()
    for item in data:
        if item["path"] == path:
            item["usage_score"] = item.get("usage_score", 0) + 1
            break
    
    # Save back to file
    try:
        with open(INDEX_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving usage: {e}")

def get_latest(search_type=None):
    """Find the most recently modified file or folder."""
    data = load_index()
    if not data: return None
    
    filtered = data
    if search_type:
        filtered = [i for i in data if i["type"] == search_type]
    
    if not filtered: return None
    
    # Sort by mtime descending
    sorted_items = sorted(filtered, key=lambda x: x.get("mtime", 0), reverse=True)
    return sorted_items[0]

def open_path(path):
    """Open file or folder using OS native commands."""
    if not path or not os.path.exists(path):
        return False
    
    try:
        system = platform.system()
        if system == "Darwin": # Mac
            subprocess.run(["open", path], check=True)
        elif system == "Windows":
            os.startfile(path)
        else: # Linux/Other
            subprocess.run(["xdg-open", path], check=True)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    # Test
    p, s = smart_search("downloads", "folder")
    print(f"Path: {p}, Suggestions: {s}")