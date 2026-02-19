import sys
import json
import socket
import threading
import time
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                             QTextEdit, QFrame, QSplitter, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem,
                             QGraphicsItem, QGraphicsTextItem)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath
import pyqtgraph as pg

# --- Configuration ---
DEFAULT_DRONE_IP = "10.33.30.181" 
PORT = 5000

# --- Styles ---
DARK_STYLESHEET = """
QMainWindow { background-color: #1e1e1e; color: #ffffff; }
QWidget { background-color: #1e1e1e; color: #ffffff; font-family: 'Segoe UI'; }
QFrame { border: 1px solid #333333; border-radius: 5px; }
QPushButton { background-color: #333333; color: white; border: none; padding: 8px; border-radius: 4px; }
QPushButton:hover { background-color: #444444; }
QPushButton:pressed { background-color: #555555; }
QLineEdit { background-color: #252526; color: white; border: 1px solid #333333; padding: 5px; }
QLabel { color: #cccccc; }
QGraphicsView { background-color: #252526; border: none; }
"""

# --- Network Worker ---
class DroneClient(QThread):
    data_received = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    connection_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.ip = DEFAULT_DRONE_IP
        self.socket = None
        self.connected = False
        self.running = True
        self.command_queue = []

    def run(self):
        while self.running:
            if not self.connected:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.settimeout(2)
                    self.socket.connect((self.ip, PORT))
                    self.connected = True
                    self.connection_status.emit(True)
                    self.log_message.emit(f"Connected to {self.ip}")
                except Exception:
                    time.sleep(2)
                    continue

            try:
                # Send queued commands first
                while self.command_queue:
                    cmd = self.command_queue.pop(0)
                    self.socket.sendall(cmd.encode())
                    self.log_message.emit(f">> Sent: {cmd}")
                    # Small delay to let server process
                    time.sleep(0.1)

                # Poll Data
                self.socket.sendall(b"GET_DATA")
                data = self.socket.recv(4096)
                if data:
                    text = data.decode()
                    if text.startswith("{"):
                        try:
                            telem = json.loads(text)
                            self.data_received.emit(telem)
                        except: pass
                    elif text.startswith("ACK") or text.startswith("ERR"):
                        self.log_message.emit(f"<< Drone: {text}")
            
            except Exception as e:
                self.log_message.emit(f"Connection Error: {e}")
                self.connected = False
                self.connection_status.emit(False)
                if self.socket: self.socket.close()
            
            time.sleep(0.1) # 10Hz Update

    def send_command(self, cmd):
        self.command_queue.append(cmd)

    def set_ip(self, ip):
        self.ip = ip
        if self.connected:
            self.connected = False
            if self.socket: self.socket.close()

# --- Visual Mission Block ---
class MissionBlock(QGraphicsRectItem):
    def __init__(self, name, x, y, command):
        super().__init__(0, 0, 120, 60)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("#333333")))
        self.setPen(QPen(QColor("#007acc"), 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        
        self.command = command
        self.name = name
        
        # Label
        self.text = QGraphicsTextItem(name, self)
        self.text.setDefaultTextColor(Qt.white)
        self.text.setPos(10, 20)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.scene().update_connections()

# --- Mission Scene ---
class MissionScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blocks = []
        self.connections = [] # List of tuples (start_block, end_block)
        self.temp_line = None

    def add_block(self, name, command):
        # Stagger position
        x = 50 + len(self.blocks) * 140
        y = 100
        block = MissionBlock(name, x, y, command)
        self.addItem(block)
        self.blocks.append(block)
        
        # Auto-connect to previous block if exists
        if len(self.blocks) > 1:
            prev = self.blocks[-2]
            self.connections.append((prev, block))
            self.update_connections()

    def update_connections(self):
        # Clear old lines
        for item in self.items():
            if isinstance(item, QGraphicsPathItem):
                self.removeItem(item)
        
        # Draw new lines
        for start, end in self.connections:
            path = QPainterPath()
            start_pt = start.pos() + QPointF(120, 30) # Right center
            end_pt = end.pos() + QPointF(0, 30)     # Left center
            
            path.moveTo(start_pt)
            # Cubic bezier for smooth curve
            ctrl1 = start_pt + QPointF(50, 0)
            ctrl2 = end_pt - QPointF(50, 0)
            path.cubicTo(ctrl1, ctrl2, end_pt)
            
            line = QGraphicsPathItem(path)
            line.setPen(QPen(QColor("#666666"), 2))
            self.addItem(line)

    def get_mission_sequence(self):
        return [b.command for b in self.blocks]

# --- Main Window ---
class AdvancedDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASCEND Advanced Mission Planner")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

        # Network Client
        self.client = DroneClient()
        self.client.data_received.connect(self.update_telemetry)
        self.client.log_message.connect(self.log)
        self.client.connection_status.connect(self.update_connection_led)
        self.client.start()

        # Telemetry History
        self.history_alt = [0]*100
        self.history_bat = [0]*100
        self.ptr = 0

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # --- Top Bar (Connection & Status) ---
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        tb_layout = QHBoxLayout(top_bar)
        
        self.led = QLabel("●")
        self.led.setStyleSheet("color: red; font-size: 20px;")
        tb_layout.addWidget(self.led)
        
        self.ip_input = QLineEdit(DEFAULT_DRONE_IP)
        self.ip_input.setFixedWidth(120)
        tb_layout.addWidget(self.ip_input)
        
        btn_connect = QPushButton("Update IP")
        btn_connect.clicked.connect(lambda: self.client.set_ip(self.ip_input.text()))
        tb_layout.addWidget(btn_connect)
        
        tb_layout.addStretch()
        
        self.lbl_mode = QLabel("MODE: UNKNOWN")
        self.lbl_mode.setStyleSheet("font-weight: bold; font-size: 14px; color: orange;")
        tb_layout.addWidget(self.lbl_mode)
        
        self.lbl_bat = QLabel("BAT: 0.0V")
        self.lbl_bat.setStyleSheet("font-weight: bold; font-size: 14px; color: #4caf50;")
        tb_layout.addWidget(self.lbl_bat)

        layout.addWidget(top_bar)

        # --- Main Splitter (Visual Planner vs Charts) ---
        splitter = QSplitter(Qt.Horizontal)
        
        # LEFT: Visual Mission Builder
        mission_frame = QFrame()
        mf_layout = QVBoxLayout(mission_frame)
        
        # Palette
        palette = QHBoxLayout()
        btn_add_to = QPushButton("+ TAKEOFF")
        btn_add_to.clicked.connect(lambda: self.scene.add_block("TAKEOFF (1m)", "TAKEOFF"))
        palette.addWidget(btn_add_to)
        
        btn_add_mv = QPushButton("+ MOVE N")
        btn_add_mv.clicked.connect(lambda: self.scene.add_block("MOVE NORTH", "MOVE_N")) # Example
        palette.addWidget(btn_add_mv)
        
        btn_add_lnd = QPushButton("+ LAND")
        btn_add_lnd.clicked.connect(lambda: self.scene.add_block("LAND", "LAND"))
        palette.addWidget(btn_add_lnd)
        
        btn_clear = QPushButton("CLEAR")
        btn_clear.setStyleSheet("color: #f44336;")
        btn_clear.clicked.connect(self.clear_mission)
        palette.addWidget(btn_clear)
        
        mf_layout.addLayout(palette)
        
        # Canvas
        self.scene = MissionScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        mf_layout.addWidget(self.view)
        
        # Execute Bar
        exec_layout = QHBoxLayout()
        btn_arm = QPushButton("ARM DRONE")
        btn_arm.setStyleSheet("background-color: #ff9800; color: black; font-weight: bold;")
        btn_arm.clicked.connect(lambda: self.client.send_command("ARM"))
        exec_layout.addWidget(btn_arm)
        
        btn_run = QPushButton("UPLOAD & RUN MISSION")
        btn_run.setStyleSheet("background-color: #007acc; font-weight: bold;")
        btn_run.clicked.connect(self.run_mission)
        exec_layout.addWidget(btn_run)
        
        btn_kill = QPushButton("KILL SWITCH")
        btn_kill.setStyleSheet("background-color: #f44336; font-weight: bold;")
        btn_kill.clicked.connect(lambda: self.client.send_command("DISARM"))
        exec_layout.addWidget(btn_kill)
        
        mf_layout.addLayout(exec_layout)
        
        splitter.addWidget(mission_frame)

        # RIGHT: Telemetry Charts & Logs
        right_frame = QFrame()
        rf_layout = QVBoxLayout(right_frame)
        
        # Charts
        self.chart_alt = pg.PlotWidget(title="Altitude (m)")
        self.chart_alt.setBackground("#252526")
        self.curve_alt = self.chart_alt.plot(pen=pg.mkPen('#007acc', width=2))
        rf_layout.addWidget(self.chart_alt)
        
        # Logs
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #111; color: #0f0; font-family: Consolas;")
        rf_layout.addWidget(self.log_view)
        
        splitter.addWidget(right_frame)
        splitter.setSizes([700, 400]) # 70% left, 30% right
        
        
        layout.addWidget(splitter)

    def update_connection_led(self, status):
        self.led.setStyleSheet(f"color: {'#4caf50' if status else 'red'}; font-size: 20px;")

    def update_telemetry(self, data):
        # Update Labels
        self.lbl_mode.setText(f"MODE: {data.get('mode', 'UNK')}")
        self.lbl_bat.setText(f"BAT: {data.get('bat_v', 0)}V")
        
        # Update Charts
        self.history_alt = self.history_alt[1:] + [data.get('alt', 0)]
        self.curve_alt.setData(self.history_alt)
        
        # Log specific errors
        if "last_error" in data and data["last_error"]:
            self.log(f"!! {data['last_error']}")

    def log(self, msg):
        self.log_view.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def clear_mission(self):
        self.scene.blocks.clear()
        self.scene.connections.clear()
        self.scene.clear()

    def run_mission(self):
        sequence = self.scene.get_mission_sequence()
        if not sequence:
            self.log("Error: Empty Mission")
            return
        
        self.log(f"Uploading Sequence: {sequence}")
        # Send one by one (Simple logic for now)
        for cmd in sequence:
            self.client.send_command(cmd)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedDashboard()
    window.show()
    sys.exit(app.exec_())