import datetime
import os
import platform
import webbrowser
from core.state_manager import shared_state
from features.utils import (
    open_notepad, open_chrome, open_file, close_app, 
    open_url, system_command, close_window
)
from features.file_index import smart_search, open_path, increment_usage, get_latest
from features.indexer import build_index
from core.memory import remember, recall
from features.voice import speak, listen, wait_until_finished
from features.ai import ask_ai

# 🧠 Smart Upgrade Modules
from features.context_manager import context
from features.automation import automation
from features.window_control import window_manager
from features.automation_utils import automation_tools

# 🌐 Global Platform Mappings
WEBSITES = {
    "google": {"home": "https://www.google.com", "search": "https://www.google.com/search?q={}"},
    "youtube": {"home": "https://www.youtube.com", "search": "https://www.youtube.com/results?search_query={}"},
    "github": {"home": "https://www.github.com", "search": "https://github.com/search?q={}"},
    "amazon": {"home": "https://www.amazon.com", "search": "https://www.amazon.com/s?k={}"},
    "instagram": {"home": "https://www.instagram.com"},
    "facebook": {"home": "https://www.facebook.com"},
    "chatgpt": {"home": "https://chat.openai.com"},
}

# 🧠 HELPER FUNCTIONS FOR SELECTION
def parse_number(text):
    """Convert spoken numbers to integers."""
    numbers = {
        "one": 1, "first": 1, "1st": 1, "two": 2, "second": 2, "2nd": 2,
        "three": 3, "third": 3, "3rd": 3, "four": 4, "fourth": 4, "4th": 4, "five": 5, "fifth": 5, "5th": 5
    }
    text = text.strip().lower()
    if text.isdigit(): return int(text)
    return numbers.get(text, None)

def get_user_choice(matches):
    """Interaction loop to let user select from multiple results via voice and UI."""
    if not matches: return None
    if len(matches) == 1: return matches[0]["path"]

    # 1. Push to UI shared state for visual display
    shared_state.set("search_results", matches)

    # 2. Limit to top 5 for manageable speech
    matches = matches[:5]
    speak_text = f"I found {len(matches)} results. "
    for i, m in enumerate(matches):
        speak_text += f"Number {i+1}. {m['name']}. "
    
    speak(speak_text)
    wait_until_finished()
    
    retries = 2
    while retries > 0:
        speak("Please say the number you want to open.")
        wait_until_finished()
        choice_text = listen()
        
        if not choice_text or choice_text in ["cancel", "nothing", "stop"]:
            speak("Selection cancelled.")
            shared_state.clear_results()
            return None
            
        index = parse_number(choice_text)
        if index and 1 <= index <= len(matches):
            shared_state.clear_results()
            return matches[index-1]["path"]
        
        retries -= 1
        if retries > 0:
            speak("I didn't catch that. Please say a valid number.")
            wait_until_finished()
        
    speak("Maximum retries reached. Operation cancelled.")
    shared_state.clear_results()
    return None

def parse_command(command):
    """
    Cleans natural language input and extracts intent + target.
    """
    cmd = command.lower().strip()
    
    fillers = {
        "please", "can", "you", "could", "would", "shall", "should", "show", 
        "my", "the", "me", "navigate", "to", "find", "search", "for", "look", 
        "give", "launch", "start", "run", "at", "go", "is", "a", "an", "this",
        "assistant", "hey", "jarvis", "tell", "what"
    }
    
    intent = "unknown"
    if "exit" in cmd or "stop" in cmd or "bye" in cmd: intent = "exit"
    elif "minimize" in cmd: intent = "minimize"
    elif "maximize" in cmd: intent = "maximize"
    elif "close" in cmd: intent = "close"
    elif "update file index" in cmd or "rebuild index" in cmd: return {"intent": "update_index", "target": ""}
    elif "time" in cmd: return {"intent": "get_time", "target": ""}
    elif "open" in cmd: 
        if "file" in cmd: intent = "open_file"
        elif "folder" in cmd or "directory" in cmd: intent = "open_folder"
        else: intent = "open"
    elif "file" in cmd: intent = "open_file"
    elif "folder" in cmd or "directory" in cmd: intent = "open_folder"
    elif "find" in cmd or "search" in cmd: intent = "find"
    elif "write" in cmd or "type" in cmd:
        intent = "write"
        # Payload extraction for typing
        trigger = "write" if "write" in cmd else "type"
        target = cmd.split(trigger, 1)[1].strip()
        return {"intent": intent, "target": target}
    elif "save" in cmd: intent = "save"

    words = cmd.split()
    keywords = {"file", "folder", "directory", "find", "search", "open", "close", "window", "minimize", "maximize"}
    target_words = [w for w in words if w not in fillers and w not in keywords]
    target = " ".join(target_words).strip()
        
    return {"intent": intent, "target": target}

def shutdown():
    """Forces an immediate global shutdown."""
    print("Shutdown triggered")
    speak("Goodbye")
    
    # Send the global stop signal to kill VoiceWorker
    print("Stopping threads")
    from core.state_manager import stop_event
    stop_event.set()
    
    # Stop TTS Engine gracefully to prevent trailing speech loops
    try:
        from features.voice import engine
        if engine: engine.stop()
    except:
        pass
        
    print("Exiting app")
    
    # Try closing PyQt6 UI safely
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app: app.quit()
    except:
        pass
        
    # Failsafe guarantee process elimination
    import os
    os._exit(0)

def handle_command(command):
    """
    Dynamic command router with multi-step support and context awareness.
    """
    # 🔗 Multi-Step Splitter
    steps = []
    if " and " in command.lower():
        steps = command.lower().split(" and ")
    elif " then " in command.lower():
        steps = command.lower().split(" then ")
    else:
        steps = [command]

    final_success = True
    last_response = ""

    for step in steps:
        # 🤖 Automation Check
        actions = automation.get_actions(step)
        if actions:
            speak(f"Starting automation for {step}.")
            for a in actions:
                handle_command(a)
            continue

        parsed = parse_command(step)
        intent = parsed["intent"]
        target = context.resolve(parsed["target"])
        
        print(f"DEBUG: Parsed Intent -> {intent} | Target -> {target}")
        
        response = ""

        # 🛑 1. EXIT
        if intent == "exit":
            shutdown()
            return False, "Exit"

        # 📉 2. WINDOW CONTROL
        elif intent == "minimize":
            window_manager.minimize()
            speak("Minimizing active window.")
            continue
        elif intent == "maximize":
            window_manager.maximize()
            speak("Maximizing window.")
            continue

        # ✍️ 3. AUTO WRITING
        elif intent == "write":
            if target:
                speak(f"Writing: {target[:20]}...")
                # Auto-focus delay if it was part of a multi-step "open and write"
                delay = 2.0 if len(steps) > 1 else 0.5
                if automation_tools.type_smart(target, delay=delay):
                    response = "Text written successfully."
                else:
                    response = "I encountered an error while typing."
                    speak(response)
            continue

        elif intent == "save":
            automation_tools.save_current()
            speak("Saving current progress.")
            continue

        # 📁 3. FILE/FOLDER OPERATIONS
        elif intent in ["open_file", "open_folder", "open"]:
            # Special check for "latest" or "recent"
            if "latest" in step or "recent" in step:
                t_filter = "file" if "file" in step else "folder" if "folder" in step else None
                latest_item = get_latest(t_filter)
                if latest_item:
                    path = latest_item["path"]
                    if open_path(path):
                        speak(f"Opening latest {latest_item['type']}, {latest_item['name']}.")
                        context.update("open", path)
                        increment_usage(path)
                else:
                    speak("No recent items found.")
                continue

            # Standard Search
            s_type = "file" if intent == "open_file" else "folder" if intent == "open_folder" else None
            
            # Browser/App check for generic open
            if intent == "open":
                if target in WEBSITES:
                    open_url(WEBSITES[target]["home"])
                    speak(f"Opening {target}.")
                    continue
                if target == "notepad": open_notepad(); continue
                if target == "chrome": open_chrome(); continue

            matches = smart_search(target, s_type)
            if not matches:
                speak(f"I could not locate any results for {target}.")
            else:
                path = get_user_choice(matches)
                if path:
                    if open_path(path):
                        speak(f"Opening {os.path.basename(path)}.")
                        context.update(intent, path)
                        increment_usage(path)
                    else: speak("Failed to open.")
            continue

        # ❌ 4. CLOSE
        elif intent == "close":
            if not target or target in ["window", "current"]:
                if window_manager.close_front():
                    speak("Closing the active window.")
                else:
                    speak("No open window found")
                    
            elif os.path.isabs(target) and os.path.exists(target):
                # Target was resolved to an absolute path via 'it' or 'that' memory context
                if window_manager.close_last(target):
                    speak(f"Closing {os.path.basename(target)}.")
                else:
                    speak("No open window found")
            else:
                # Direct name target: e.g., "close downloads" or "close chrome"
                if "folder" in step:
                    clean_target = target.replace("folder", "").strip() or "folder"
                    if window_manager.close_folder(clean_target):
                        speak(f"Closing folder {clean_target}.")
                    else:
                        speak("No open window found")
                else:
                    # Generic close: try both app and folder safely
                    closed_app = window_manager.close_application(target)
                    closed_folder = window_manager.close_folder(target)
                    
                    if closed_app or closed_folder:
                        speak(f"Closing {target}.")
                    else:
                        speak("No open window found")
            
            # Clear context just in case
            context.last_entity = None
            continue

        # 🕒 5. SYSTEM
        elif intent == "update_index":
            speak("Updating index.")
            build_index(); continue
        elif intent == "get_time":
            speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}"); continue

        # 🤖 6. AI FALLBACK
        else:
            response = ask_ai(step)
            if response: speak(response)

    return True, last_response