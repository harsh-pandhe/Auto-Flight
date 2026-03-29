import tkinter as tk
from tkinter import scrolledtext
import socket
import json
import threading
import time
from datetime import datetime
import csv

# --- Configuration ---
# REPLACE THIS WITH THE IP YOU FOUND USING `hostname -I` ON THE PI
DEFAULT_DRONE_IP = "10.33.30.181" 
PORT = 5000

# --- Styles ---
COLOR_BG = "#1e1e1e"
COLOR_FG = "#ffffff"
COLOR_BTN_BG = "#333333"
COLOR_ACCENT = "#007acc"

class MissionDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCEND Mission Control (Remote)")
        self.root.geometry("950x700")
        self.root.configure(bg=COLOR_BG)

        self.socket = None
        self.connected = False
        self.running = True
        self.logging_active = False
        self.csv_file = None
        self.csv_writer = None

        self.telemetry_data = {
            "bat_v": 0.0, "bat_p": 0, "gps_sats": 0, "gps_fix": "None",
            "alt": 0.0, "roll": 0.0, "pitch": 0.0, "yaw": 0.0,
            "mode": "UNKNOWN", "armed": False, "status": "Disconnected"
        }

        self.setup_ui()
        
        # Start Data Polling Thread
        self.poll_thread = threading.Thread(target=self.poll_data_loop, daemon=True)
        self.poll_thread.start()

    def setup_ui(self):
        # Header
        tk.Label(self.root, text="MISSION CONTROL - REMOTE LINK", font=("Segoe UI", 18, "bold"), bg=COLOR_BG, fg=COLOR_ACCENT).pack(pady=10)

        # Main Layout
        main_frame = tk.Frame(self.root, bg=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20)

        left_col = tk.Frame(main_frame, bg=COLOR_BG)
        left_col.pack(side=tk.LEFT, fill="both", expand=True, padx=(0,10))
        
        right_col = tk.Frame(main_frame, bg=COLOR_BG)
        right_col.pack(side=tk.RIGHT, fill="both", expand=True, padx=(10,0))

        # --- Connection Panel ---
        frame_conn = tk.LabelFrame(left_col, text="LINK CONFIG", bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_conn.pack(fill="x", pady=5)
        
        self.entry_ip = tk.Entry(frame_conn, bg="#333", fg="white", font=("Consolas", 11), justify="center")
        self.entry_ip.insert(0, DEFAULT_DRONE_IP)
        self.entry_ip.pack(fill="x", padx=5, pady=5)
        
        self.btn_connect = tk.Button(frame_conn, text="CONNECT", bg="#444", fg="white", font=("Segoe UI", 10, "bold"), command=self.connect_socket_thread)
        self.btn_connect.pack(fill="x", padx=5, pady=5)

        # --- Logging ---
        self.btn_log = tk.Button(left_col, text="START LOGGING", bg="#444", fg="white", font=("Segoe UI", 10), command=self.toggle_logging)
        self.btn_log.pack(fill="x", pady=10)

        # --- Controls ---
        frame_ctrl = tk.LabelFrame(left_col, text="FLIGHT DECK", bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_ctrl.pack(fill="x", pady=5)
        
        self.create_btn(frame_ctrl, "ARM", "orange", "black", lambda: self.send_command("ARM"))
        self.create_btn(frame_ctrl, "TAKEOFF (1m)", "green", "white", lambda: self.send_command("TAKEOFF"))
        self.create_btn(frame_ctrl, "LAND", "blue", "white", lambda: self.send_command("LAND"))
        self.create_btn(frame_ctrl, "DISARM (KILL)", "red", "white", lambda: self.send_command("DISARM"))

        # --- Telemetry ---
        frame_telem = tk.LabelFrame(right_col, text="LIVE TELEMETRY", bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_telem.pack(fill="x", pady=5)

        self.lbl_status = self.make_telem_row(frame_telem, "System Status", "Disconnected", "gray")
        self.lbl_bat = self.make_telem_row(frame_telem, "Battery", "0.0 V | 0%")
        self.lbl_gps = self.make_telem_row(frame_telem, "GPS", "0 Sats (None)")
        self.lbl_alt = self.make_telem_row(frame_telem, "Altitude", "0.00 m")
        self.lbl_att = self.make_telem_row(frame_telem, "Attitude", "R:0 P:0 Y:0")
        self.lbl_mode = self.make_telem_row(frame_telem, "Flight Mode", "UNKNOWN")
        self.lbl_arm = self.make_telem_row(frame_telem, "Arm State", "DISARMED", "red")

        # --- Log Console ---
        tk.Label(right_col, text="EVENT LOG", bg=COLOR_BG, fg="gray", anchor="w").pack(fill="x", pady=(10,0))
        self.console = scrolledtext.ScrolledText(right_col, height=15, bg="#111", fg="#0f0", font=("Consolas", 9))
        self.console.pack(fill="both", expand=True)

    def create_btn(self, parent, text, bg, fg, cmd):
        tk.Button(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 10, "bold"), 
                 relief="flat", padx=10, pady=5, command=cmd).pack(fill="x", padx=5, pady=2)

    def make_telem_row(self, parent, label, value, fg="white"):
        f = tk.Frame(parent, bg=COLOR_BG)
        f.pack(fill="x", padx=5, pady=2)
        tk.Label(f, text=label, width=15, anchor="w", bg=COLOR_BG, fg="#888", font=("Consolas", 11)).pack(side=tk.LEFT)
        l = tk.Label(f, text=value, anchor="e", bg=COLOR_BG, fg=fg, font=("Consolas", 11, "bold"))
        l.pack(side=tk.RIGHT, expand=True, fill="x")
        return l

    # --- Logic ---
    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.console.see(tk.END)

    def connect_socket_thread(self):
        threading.Thread(target=self.connect_socket, daemon=True).start()

    def connect_socket(self):
        ip = self.entry_ip.get()
        self.log(f"Connecting to {ip}:{PORT}...")
        self.btn_connect.config(bg="orange", text="CONNECTING...")
        
        try:
            if self.socket: self.socket.close()
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(3)
            self.socket.connect((ip, PORT))
            self.connected = True
            self.btn_connect.config(bg="green", text="CONNECTED")
            self.log("SUCCESS: Link Established")
        except Exception as e:
            self.log(f"Connection Failed: {e}")
            self.btn_connect.config(bg="red", text="FAILED")
            self.connected = False

    def send_command(self, cmd):
        if not self.connected:
            self.log("Error: Not Connected")
            return
        try:
            self.socket.sendall(cmd.encode())
            self.log(f">> Sent Command: {cmd}")
        except Exception as e:
            self.log(f"Send Error: {e}")
            self.connected = False
            self.btn_connect.config(bg="red", text="LINK LOST")

    def poll_data_loop(self):
        while self.running:
            if self.connected and self.socket:
                try:
                    self.socket.sendall(b"GET_DATA")
                    data = self.socket.recv(4096)
                    
                    if data:
                        text = data.decode()
                        if text.startswith("ACK") or text.startswith("ERR"):
                            self.root.after(0, self.log, f"<< Drone: {text}")
                        elif text.startswith("{"):
                            try:
                                telem = json.loads(text)
                                self.telemetry_data = telem
                                self.root.after(0, self.update_ui)
                                if self.logging_active: self.write_log(telem)
                            except: pass
                except Exception as e:
                    pass # Transient network errors are ignored in poll loop
            time.sleep(0.1)

    def update_ui(self):
        data = self.telemetry_data
        self.lbl_status.config(text=data.get('status', 'Unknown'), fg="cyan")
        self.lbl_bat.config(text=f"{data.get('bat_v',0)} V | {data.get('bat_p',0)}%")
        self.lbl_gps.config(text=f"{data.get('gps_sats',0)} Sats ({data.get('gps_fix','None')})")
        self.lbl_alt.config(text=f"{data.get('alt',0)} m")
        self.lbl_att.config(text=f"R:{data.get('roll',0)} P:{data.get('pitch',0)} Y:{data.get('yaw',0)}")
        self.lbl_mode.config(text=data.get('mode', 'UNKNOWN'))
        
        if data.get('armed', False):
            self.lbl_arm.config(text="ARMED", fg="#0f0")
        else:
            self.lbl_arm.config(text="DISARMED", fg="red")

    def toggle_logging(self):
        if not self.logging_active:
            filename = f"mission_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                self.csv_file = open(filename, 'w', newline='')
                self.csv_writer = csv.writer(self.csv_file)
                self.csv_writer.writerow(["Timestamp", "Bat_V", "Bat_P", "GPS_Sats", "Alt", "Roll", "Pitch", "Yaw", "Mode", "Armed"])
                self.logging_active = True
                self.btn_log.config(text="STOP LOGGING", bg="red")
                self.log(f"Logging started: {filename}")
            except Exception as e: self.log(f"Log Error: {e}")
        else:
            self.logging_active = False
            if self.csv_file: self.csv_file.close()
            self.btn_log.config(text="START LOGGING", bg="#444")
            self.log("Logging stopped.")

    def write_log(self, data):
        if self.csv_writer:
            try:
                self.csv_writer.writerow([
                    datetime.now().strftime('%H:%M:%S.%f'),
                    data.get('bat_v'), data.get('bat_p'),
                    data.get('gps_sats'), data.get('alt'),
                    data.get('roll'), data.get('pitch'), data.get('yaw'),
                    data.get('mode'), data.get('armed')
                ])
                self.csv_file.flush()
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = MissionDashboard(root)
    root.mainloop()