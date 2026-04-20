import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import platform
import subprocess
import logging
from core.state_manager import shared_state, logger

# 🔊 Global State Control
speech_queue = queue.Queue()
stop_event = threading.Event()
is_speaking = False  # Global guard flag to prevent self-interruption
os_name = platform.system()

def tts_worker():
    """Dedicated background thread for TTS output."""
    global is_speaking
    
    engine = None
    if os_name != "Darwin":
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 185)
            engine.setProperty('volume', 1.0)
        except Exception as e:
            logger.error(f"TTS Engine Init Error: {e}")

    while True:
        try:
            text = speech_queue.get(timeout=0.1)
            if text == "SHUTDOWN_WORKER":
                break
            
            if text:
                logger.info(f"Jarvis Speaking: {text}")
                # ⚔️ Protection: Mark as speaking immediately
                is_speaking = True
                
                if os_name == "Darwin":
                    # macOS high-performance voice
                    subprocess.run(["say", text])
                elif engine:
                    # Windows/Linux fallback
                    if not stop_event.is_set():
                        engine.say(text)
                        engine.runAndWait()
                
                # Reset only after speech is fully finished
                is_speaking = False
                stop_event.clear()
            
            speech_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"TTS Worker Error: {e}")
            is_speaking = False
        finally:
            if speech_queue.empty():
                is_speaking = False

def wait_until_finished():
    """Wait for all pending speech to be completed."""
    while not speech_queue.empty():
        time.sleep(0.05)
    while is_speaking:
        time.sleep(0.05)

# Start background worker
threading.Thread(target=tts_worker, daemon=True).start()

def speak(text):
    """Safely queue text and stop listening interference."""
    global is_speaking
    stop_speaking()
    with speech_queue.mutex:
        speech_queue.queue.clear()
    speech_queue.put(text)

def stop_speaking():
    """Immediately kill current audio output."""
    global is_speaking
    if is_speaking:
        stop_event.set()
        if os_name == "Darwin":
            subprocess.run(["pkill", "say"])

def get_best_microphone():
    """
    Detect and return the best available microphone object.
    """
    try:
        mics = sr.Microphone.list_microphone_names()
        logger.info(f"Available Microphones: {mics}")
        
        if not mics:
            logger.error("No microphones found on the system.")
            return None

        # Look for typical preferred devices
        preferred_keywords = ["internal", "external", "usb", "core audio"]
        for keyword in preferred_keywords:
            for i, mic_name in enumerate(mics):
                if keyword in mic_name.lower():
                    logger.info(f"Selected Preferred Mic: {mic_name} (Index {i})")
                    return sr.Microphone(device_index=i)

        logger.info("Using default system microphone.")
        return sr.Microphone()
    except Exception as e:
        logger.error(f"Error during microphone detection: {e}")
        return None

def listen(timeout=5, phrase_time_limit=5):
    """
    Intelligent ear module with 4-layer state protection and robust mic detection.
    """
    global is_speaking
    from core.state_manager import stop_event as global_stop
    
    # ❌ GUARD 1: Instant block if speaking or shutting down
    if is_speaking or global_stop.is_set(): return ""
    
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 300
    r.pause_threshold = 1.3
    r.non_speaking_duration = 0.8
    
    mic = get_best_microphone()
    if not mic:
        shared_state.log_error("Microphone Hardware Missing or Occupied")
        return ""

    try:
        with mic as source:
            # ❌ GUARD 2: Multi-check before opening hardware
            if is_speaking or global_stop.is_set(): return ""
            
            logger.info("Jarvis is listening...")
            r.adjust_for_ambient_noise(source, duration=0.6)
            
            # ❌ GUARD 3: Multi-check before capturing
            if is_speaking or global_stop.is_set(): return ""
            
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # ❌ GUARD 4: Final check after capturing
            if is_speaking or global_stop.is_set(): return ""
            
            logger.info("Jarvis is recognizing...")
            query = r.recognize_google(audio, language='en-in')
            logger.info(f"Recognized: {query}")
            return query.lower()
            
    except sr.WaitTimeoutError:
        return ""
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        shared_state.log_error(f"Recognition Service Error: {e}")
        return ""
    except Exception as e:
        shared_state.log_error(f"Microphone Logic Error: {e}")
        return ""