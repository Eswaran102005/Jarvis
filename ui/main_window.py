import sys
import time
import math
import random
import logging
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QMessageBox
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient, QFont, QLinearGradient

# Backend Integration
from features.commands import handle_command
from features.voice import speak, listen, wait_until_finished
from core.state_manager import shared_state, logger

class VoiceWorker(QThread):
    """
    Background worker that runs the JARVIS voice-logic loop.
    Communicates with the GUI via shared_state.
    """
    state_changed = pyqtSignal(dict)

    def run(self):
        logger.info("VoiceWorker thread started.")
        # Initial boot speak
        try:
            shared_state.set("status", "speaking")
            shared_state.set("assistant_text", "Neural link active. Core systems online.")
            speak("Systems operational. JARVIS is online.")
            wait_until_finished()
        except Exception as e:
            logger.error(f"Boot Speech Failed: {e}")

        # Import the global stop event flag
        from core.state_manager import stop_event

        while not stop_event.is_set():
            try:
                # 1. Reset for listening
                shared_state.clear_results()
                shared_state.set("status", "idle")
                self.state_changed.emit(shared_state.get_all())

                # 🎙️ LISTENING
                command = listen()
                if not command: continue

                # Process Wake Word
                if "hey jarvis" in command or "jarvis" in command or "assistant" in command:
                    shared_state.set("status", "listening")
                    shared_state.set("user_text", command)
                    self.state_changed.emit(shared_state.get_all())
                    speak("Go ahead.")
                    command = listen()

                if command:
                    shared_state.set("user_text", command)
                    shared_state.set("status", "thinking")
                    self.state_changed.emit(shared_state.get_all())
                    
                    # Execute Command
                    try:
                        success, response = handle_command(command)
                        if response:
                            shared_state.set("assistant_text", response)
                            shared_state.set("status", "speaking")
                            self.state_changed.emit(shared_state.get_all())
                            wait_until_finished()
                    except Exception as cmd_e:
                        logger.error(f"Command execution failed: {cmd_e}")
                        shared_state.log_error(f"Execution Error: {cmd_e}")
                        speak("I encountered an error processing that request.")
                    
                    shared_state.set("status", "idle")
                    self.state_changed.emit(shared_state.get_all())
                    time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"Worker Loop Error: {e}")
                shared_state.log_error(f"Critical Worker Error: {e}")
                time.sleep(2)

class ResultsPanel(QFrame):
    """
    Sliding/Fading panel for search results.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 200)
        self.setStyleSheet("""
            QFrame {
                background: rgba(0, 20, 40, 0.9);
                border: 1px solid #00ffff;
                border-radius: 12px;
            }
            QLabel {
                color: #00ffff;
                font-family: 'Inter';
                font-size: 11px;
            }
        """)
        self.layout = QVBoxLayout(self)
        self.title = QLabel("SYSTEM_DIAGNOSTICS")
        self.title.setStyleSheet("font-weight: bold; font-size: 12px; border-bottom: 1px solid #00ffff;")
        self.layout.addWidget(self.title)
        
        self.content = QLabel("No active issues.")
        self.content.setWordWrap(True)
        self.layout.addWidget(self.content)
        
        self.hide()

    def display(self, results):
        if not results:
            self.hide()
            return

        text = ""
        for i, res in enumerate(results[:5]):
            name = res['path'].split('/')[-1]
            text += f"{i+1}. {name}\n"
        
        self.content.setText(text)
        self.show()
        
        if self.parent():
            self.move(self.parent().width() - 310, 50)
            QTimer.singleShot(8000, self.hide)

class AIFaceWidget(QWidget):
    """
    Futuristic AI Face with animated eyes and mouth waveform.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 250)
        self.status = "idle"
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)
        
        self.pulse = 0.0
        self.eye_scale = 1.0
        self.mouth_waves = [0.0] * 20
        self.eye_offset = QPoint(0, 0)
        self.blink_factor = 1.0
        self.wave_phase = 0.0

    def update_animation(self):
        self.pulse += 0.05
        self.wave_phase += 0.2
        
        if self.status == "idle":
            self.eye_scale = 1.0 + 0.05 * math.sin(self.pulse)
            self.blink_factor = 1.0 if random.random() > 0.02 else 0.1
            self.eye_offset = QPoint(0, 0)
            for i in range(len(self.mouth_waves)):
                self.mouth_waves[i] *= 0.9 

        elif self.status == "listening":
            self.eye_scale = 1.2 + 0.1 * math.sin(self.pulse * 2)
            self.blink_factor = 1.0
            
        elif self.status == "thinking":
            self.eye_scale = 1.0
            self.eye_offset = QPoint(int(10 * math.sin(self.pulse * 1.5)), 0)
            self.blink_factor = 1.0
            
        elif self.status == "speaking":
            self.eye_scale = 1.05
            for i in range(len(self.mouth_waves)):
                self.mouth_waves[i] = math.sin(self.wave_phase + i * 0.5) * random.uniform(10, 40)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        base_cyan = QColor(0, 255, 255)
        
        if self.status == "thinking":
            base_cyan = QColor(255, 255, 100)
        elif self.status == "error":
            base_cyan = QColor(255, 50, 50)
            
        eye_spacing = 100
        eye_size = 40 * self.eye_scale
        
        for offset_x in [-eye_spacing, eye_spacing]:
            gradient = QRadialGradient(center_x + offset_x + self.eye_offset.x(), center_y - 20, eye_size)
            gradient.setColorAt(0, base_cyan)
            gradient.setColorAt(0.5, base_cyan.darker(150))
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center_x + offset_x + self.eye_offset.x() - int(eye_size//2),
                                center_y - 20 - int((eye_size * self.blink_factor)//2),
                                int(eye_size), int(eye_size * self.blink_factor))

        if self.status != "idle" or any(w > 1.0 for w in self.mouth_waves):
            pen = QPen(base_cyan, 3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            wave_width = 150
            num_points = len(self.mouth_waves)
            step = wave_width // num_points
            for i in range(num_points - 1):
                p1 = QPoint(center_x - wave_width//2 + i*step, center_y + 60 + int(self.mouth_waves[i]))
                p2 = QPoint(center_x - wave_width//2 + (i+1)*step, center_y + 60 + int(self.mouth_waves[i+1]))
                painter.drawLine(p1, p2)

class JarvisWindow(QMainWindow):
    """
    Main HUD window with integrated diagnostics and status monitoring.
    """
    def __init__(self):
        super().__init__()
        logger.info("Initializing JarvisWindow UI.")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 450)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setStyleSheet("color: #00ffff; font-family: 'Inter'; font-size: 24px; font-weight: bold;")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.clock_label)
        
        self.face = AIFaceWidget()
        self.layout.addWidget(self.face)

        self.results_panel = ResultsPanel(self)
        
        self.status_label = QLabel("[ SYSTEM_STANDBY ]")
        self.status_label.setStyleSheet("color: white; font-family: 'Inter'; font-size: 14px; letter-spacing: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        self.transcript_label = QLabel("NEURAL_LINK READY")
        self.transcript_label.setStyleSheet("color: rgba(0, 255, 255, 0.5); font-family: 'Inter'; font-size: 10px;")
        self.transcript_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.transcript_label)

        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui_state)
        self.ui_timer.start(100)
        
        self.drag_pos = None
        self.worker = VoiceWorker()
        self.worker.state_changed.connect(self.on_state_updated)
        self.worker.start()

    def update_ui_state(self):
        self.clock_label.setText(time.strftime("%H:%M:%S"))
        # Check for system errors
        state = shared_state.get_all()
        if state.get("errors"):
            last_err = state["errors"][-1]["msg"]
            self.transcript_label.setText(f"ALERT > {last_err.upper()}")
            self.face.status = "error"
        
    def on_state_updated(self, state):
        status = state.get("status", "idle")
        self.face.status = status
        display_status = status.upper() if status != "idle" else "SYSTEM_STANDBY"
        self.status_label.setText(f"[ {display_status} ]")
        
        user_txt = state.get("user_text", "")
        if user_txt:
            self.transcript_label.setText(f"USER > {user_txt.upper()}")

        results = state.get("search_results", [])
        if results:
            self.results_panel.display(results)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()
    sys.exit(app.exec())