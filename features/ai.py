import requests
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 🔧 Setup minimal logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

# 🧠 Optimized Context & Storage
chat_history = []
MAX_HISTORY = 5
response_cache = {}  

# 🌐 Persistent Session with Connection Pooling
session = requests.Session()
adapter = HTTPAdapter(max_retries=Retry(total=2, backoff_factor=0.1))
session.mount('http://', adapter)

def ask_ai(question):
    """
    High-performance AI query handler optimized for speed and reliability.
    Uses 'phi' model for low latency and maintains a tight conversation window.
    """
    global chat_history, response_cache
    
    # 🏎️ 1. Instant Cache Check
    q_lower = question.lower().strip()
    if q_lower in response_cache:
        return response_cache[q_lower]

    MODEL = "phi"  # Ultra-fast lightweight model
    URL = "http://localhost:11434/api/generate"
    
    # ⚡ Minimalist System Prompt
    system_prompt = "You are Jarvis. Keep your answers concise, intelligent, and fast."
    
    # 📚 Sliding Window History
    chat_history = chat_history[-MAX_HISTORY:]
    
    # Constructing optimized prompt
    prompt = f"System: {system_prompt}\n"
    for e in chat_history:
        prompt += f"U: {e['user']}\nA: {e['assistant']}\n"
    prompt += f"U: {question}\nA:"

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 100,  # Cap token output for speed
            "temperature": 0.7
        }
    }

    # 🔄 2. Robust Request Loop
    for attempt in range(2):
        try:
            # ⏱️ 10-second timeout ensures the app never hangs
            response = session.post(URL, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "").strip()
                
                if not answer: continue
                
                # Update Cache & History
                chat_history.append({"user": question, "assistant": answer})
                response_cache[q_lower] = answer
                
                # Cleanup cache if it grows too large
                if len(response_cache) > 50: 
                    response_cache.clear()
                
                return answer
            
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"DEBUG: AI Connection Error (Attempt {attempt+1}): {e}")
            if attempt == 0: continue

    # 🛑 3. Clean Fallback
    return "I'm having difficulty accessing my cognitive modules. Please ensure my brain (Ollama) is active."

def clear_ai_history():
    """Reset cognitive state."""
    global chat_history, response_cache
    chat_history = []
    response_cache = {}