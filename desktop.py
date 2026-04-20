import webview
import threading
import time
from app import app

def start_flask():
    """Start the flask server in a background thread."""
    app.run(port=5000, threaded=True, debug=False)

if __name__ == '__main__':
    # 1. Start Flask in the background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # 2. Wait for server to boot
    time.sleep(2)
    
    # 3. Create the desktop window
    print("Launching JARVIS Desktop Interface...")
    webview.create_window(
        'Jarvis AI Assistant', 
        'http://127.0.0.1:5000',
        width=500,
        height=700,
        resizable=True,
        min_size=(400, 600)
    )
    
    # 4. Start the GUI loop
    webview.start()
