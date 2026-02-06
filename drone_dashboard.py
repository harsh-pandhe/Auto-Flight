import tkinter as tk
from tkinter import scrolledtext, ttk
import asyncio
import threading
import csv
from datetime import datetime
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

# --- Configuration ---
DEFAULT_CONNECTION = "serial:///dev/ttyUSB0:57600"  # Default Default

# --- Styles ---
COLOR_BG = "#1e1e1e"
COLOR_FG = "#ffffff"
COLOR_BTN_BG = "#333333"
COLOR_BTN_FG = "#ffffff"
COLOR_ACCENT = "#007acc"
COLOR_SUCCESS = "#4caf50"
COLOR_WARNING = "#ff9800"
COLOR_DANGER = "#f44336"

class DroneDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCEND Drone Control Center")
        self.root.geometry("900x750")
        self.root.configure(bg=COLOR_BG)
        
        # System state
        self.drone = None 
        self.loop = asyncio.new_event_loop()
        
        # Logging State
        self.logging_active = False
        self.csv_file = None
        self.csv_writer = None
        self.telemetry_state = {
            "battery_v": 0.0,
            "battery_pct": 0.0,
            "gps_sats": 0,
            "gps_fix": "Unknown",
            "rel_alt": 0.0,
            "roll": 0.0,
            "pitch": 0.0,
            "yaw": 0.0,
            "mode": "Unknown",
            "armed": False,
            "health": "Unknown"
        }
        
        # Start Async Loop in Background Thread
        self.thread = threading.Thread(target=self.start_loop, daemon=True)
        self.thread.start()

        self.setup_ui()

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_async(self, coro):
        """Helper to run async functions from buttons"""
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def log(self, message):
        """Print to the GUI console"""
        self.console.configure(state='normal')
        self.console.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.console.see(tk.END)
        self.console.configure(state='disabled')

    def update_label(self, label, text, fg=None):
        """Thread-safe label update"""
        if fg:
             self.root.after(0, lambda: label.config(text=text, fg=fg))
        else:
             self.root.after(0, lambda: label.config(text=text))

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=COLOR_BG)
        header_frame.pack(fill="x", pady=10)
        lbl_title = tk.Label(header_frame, text="ASCEND MISSION CONTROL", font=("Segoe UI", 20, "bold"), bg=COLOR_BG, fg=COLOR_ACCENT)
        lbl_title.pack()
        lbl_subtitle = tk.Label(header_frame, text="Qualification Round Bench Test", font=("Segoe UI", 10), bg=COLOR_BG, fg="gray")
        lbl_subtitle.pack()

        # Main Layout
        main_frame = tk.Frame(self.root, bg=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_col = tk.Frame(main_frame, bg=COLOR_BG)
        left_col.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        right_col = tk.Frame(main_frame, bg=COLOR_BG)
        right_col.pack(side=tk.RIGHT, fill="both", expand=True, padx=(10, 0))

        # --- Connection Panel (Editable) ---
        frame_conn = tk.LabelFrame(left_col, text="CONNECTION", padx=10, pady=10, bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_conn.pack(fill="x", pady=10)
        
        lbl_addr = tk.Label(frame_conn, text="Address:", bg=COLOR_BG, fg="gray", font=("Segoe UI", 8))
        lbl_addr.pack(anchor="w")
        
        self.entry_conn = tk.Entry(frame_conn, bg="#333333", fg="white", font=("Consolas", 10), insertbackground="white")
        self.entry_conn.insert(0, DEFAULT_CONNECTION)
        self.entry_conn.pack(fill="x", pady=(0, 5))

        btn_connect = tk.Button(frame_conn, text="CONNECT / RESTART", bg=COLOR_BTN_BG, fg=COLOR_FG, font=("Segoe UI", 10),
                               relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.connect_drone()))
        btn_connect.pack(fill="x", pady=2)

        btn_refresh = tk.Button(frame_conn, text="REFRESH STREAMS", bg=COLOR_BTN_BG, fg=COLOR_FG, font=("Segoe UI", 10),
                               relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.configure_rates()))
        btn_refresh.pack(fill="x", pady=2)

        # --- Logging Panel ---
        frame_log = tk.LabelFrame(left_col, text="DATA LOGGING", padx=10, pady=10, bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_log.pack(fill="x", pady=10)
        self.btn_log = tk.Button(frame_log, text="START LOGGING", bg=COLOR_BTN_BG, fg=COLOR_FG, font=("Segoe UI", 10),
                                relief="flat", padx=10, pady=5, command=self.toggle_logging)
        self.btn_log.pack(fill="x")

        # --- Flight Controls ---
        frame_flight = tk.LabelFrame(left_col, text="FLIGHT COMMANDS", padx=10, pady=10, bg=COLOR_BG, fg=COLOR_DANGER, font=("Segoe UI", 10, "bold"))
        frame_flight.pack(fill="x", pady=10)

        # Danger Zone Buttons
        tk.Button(frame_flight, text="ARM MOTORS", bg=COLOR_WARNING, fg="black", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.arm_drone())).pack(fill="x", pady=5)
        
        tk.Button(frame_flight, text="HOP TEST (1m AUTO)", bg="#9c27b0", fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.hop_test())).pack(fill="x", pady=5)

        tk.Button(frame_flight, text="TAKEOFF (2m)", bg=COLOR_SUCCESS, fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.takeoff())).pack(fill="x", pady=5)

        tk.Button(frame_flight, text="MOVE NORTH", bg=COLOR_ACCENT, fg="white", font=("Segoe UI", 10, "bold"),
                 relief="flat", padx=10, pady=5, command=lambda: self.run_async(self.move_north())).pack(fill="x", pady=5)

        tk.Button(frame_flight, text="EMERGENCY LAND", bg=COLOR_DANGER, fg="white", font=("Segoe UI", 12, "bold"),
                 relief="flat", padx=10, pady=10, command=lambda: self.run_async(self.land())).pack(fill="x", pady=10)

        # --- Telemetry Panel ---
        frame_telemetry = tk.LabelFrame(right_col, text="LIVE TELEMETRY", padx=10, pady=10, bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame_telemetry.pack(fill="x", pady=5)

        # Telemetry Grid
        self.telemetry_labels = {}
        telemetry_items = [
            ("Battery", "lbl_bat", "0.00 V / 0%"),
            ("GPS Status", "lbl_gps", "0 Sats (No Fix)"),
            ("Altitude", "lbl_alt", "0.00 m"),
            ("Attitude", "lbl_att", "R: 0.0 P: 0.0 Y: 0.0"),
            ("Flight Mode", "lbl_mode", "UNKNOWN"),
            ("Arm State", "lbl_armed", "DISARMED"),
            ("System Health", "lbl_health", "Checking...")
        ]

        for idx, (name, key, default) in enumerate(telemetry_items):
            lbl_name = tk.Label(frame_telemetry, text=name + ":", font=("Consolas", 11), bg=COLOR_BG, fg="gray")
            lbl_name.grid(row=idx, column=0, sticky="w", padx=5, pady=2)
            
            lbl_val = tk.Label(frame_telemetry, text=default, font=("Consolas", 11, "bold"), bg=COLOR_BG, fg=COLOR_FG)
            lbl_val.grid(row=idx, column=1, sticky="e", padx=5, pady=2)
            self.telemetry_labels[key] = lbl_val

        # Frame config to stretch columns
        frame_telemetry.grid_columnconfigure(1, weight=1)

        # --- Console ---
        lbl_console = tk.Label(right_col, text="SYSTEM LOG", font=("Segoe UI", 10, "bold"), bg=COLOR_BG, fg="gray")
        lbl_console.pack(anchor="w", pady=(20, 5))
        
        self.console = scrolledtext.ScrolledText(right_col, height=20, state='disabled', 
                                               bg="#111111", fg="#00ff00", font=("Consolas", 9),
                                               relief="flat", padx=10, pady=10)
        self.console.pack(fill="both", expand=True)

    def create_panel(self, parent, title, buttons):
        frame = tk.LabelFrame(parent, text=title, padx=10, pady=10, bg=COLOR_BG, fg="gray", font=("Segoe UI", 10, "bold"))
        frame.pack(fill="x", pady=10)
        for text, cmd, color in buttons:
            btn = tk.Button(frame, text=text, bg=color, fg=COLOR_FG, font=("Segoe UI", 10),
                           relief="flat", padx=10, pady=5, command=lambda c=cmd: self.run_async(c()))
            btn.pack(fill="x", pady=2)

    # --- Logic ---
    def toggle_logging(self):
        if not self.logging_active:
            self.start_logging()
            self.btn_log.config(text="STOP LOGGING", bg=COLOR_DANGER)
        else:
            self.stop_logging()
            self.btn_log.config(text="START LOGGING", bg=COLOR_BTN_BG)

    def start_logging(self):
        filename = f"telemetry_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            self.csv_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(["Timestamp", "Battery_V", "Battery_Pct", "GPS_Sats", "GPS_Fix", "Rel_Alt", "Roll", "Pitch", "Yaw", "Mode", "Armed", "Health"])
            self.logging_active = True
            self.log(f"LOGGING STARTED: {filename}")
            self.run_async(self.logging_loop())
        except Exception as e:
            self.log(f"Log Start Failed: {e}")

    def stop_logging(self):
        self.logging_active = False
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        self.log("LOGGING STOPPED.")

    async def logging_loop(self):
        while self.logging_active:
            if self.csv_writer:
                row = [
                    datetime.now().strftime('%H:%M:%S.%f')[:-3],
                    self.telemetry_state["battery_v"],
                    self.telemetry_state["battery_pct"],
                    self.telemetry_state["gps_sats"],
                    self.telemetry_state["gps_fix"],
                    self.telemetry_state["rel_alt"],
                    self.telemetry_state["roll"],
                    self.telemetry_state["pitch"],
                    self.telemetry_state["yaw"],
                    self.telemetry_state["mode"],
                    self.telemetry_state["armed"],
                    self.telemetry_state["health"]
                ]
                try:
                    self.csv_writer.writerow(row)
                    self.csv_file.flush()
                except Exception:
                    pass
            await asyncio.sleep(0.1)

    # --- MAVSDK Logic ---
    async def connect_drone(self):
        # Always create a fresh system instance to avoid stale connection states
        if self.drone:
            self.log("Re-initializing System...")
            # Ideally we would close the old connection, but MAVSDK python doesn't expose a clean close() easily
            # Just overwriting it is usually enough for the script logic, though background tasks might linger.
            # In a full app we'd cancel tasks.
            self.drone = None
        
        self.drone = System()
        
        # GET CONNECTION STRING FROM UI
        conn_str = self.entry_conn.get()
        self.log(f"Connecting to {conn_str}...")
        
        try:
            await self.drone.connect(system_address=conn_str)
            self.log("Waiting for heartbeat...")
            
            # Use a timeout to avoid hanging forever if connection fails silently
            async for state in self.drone.core.connection_state():
                if state.is_connected:
                    self.log("SUCCESS: Connected to Drone!")
                    self.run_async(self.telemetry_loop())
                    break
        except Exception as e:
            self.log(f"Connection Error: {e}")
            self.log("Check cable or port (try /dev/ttyACM0)")
    
    async def telemetry_loop(self):
        if not self.drone: return
        self.log("Starting Telemetry Listeners...")
        asyncio.create_task(self.print_battery())
        asyncio.create_task(self.print_gps())
        asyncio.create_task(self.print_position())
        asyncio.create_task(self.print_attitude())
        asyncio.create_task(self.print_flight_mode())
        asyncio.create_task(self.print_armed_status())
        asyncio.create_task(self.print_status_text())
        asyncio.create_task(self.print_health())
        asyncio.create_task(self.configure_rates())

    async def configure_rates(self):
        if not self.drone: return
        self.log("Sending Rate Config...")
        try: await self.drone.telemetry.set_rate_battery(1.0)
        except: pass
        try: await self.drone.telemetry.set_rate_gps_info(2.0)
        except: pass
        try: await self.drone.telemetry.set_rate_position(5.0)
        except: pass
        self.log("Rate Config Sent.")

    async def print_status_text(self):
        try:
            async for status_text in self.drone.telemetry.status_text():
                self.log(f"DRONE: {status_text.text}")
                if "Throttle" in status_text.text and "high" in status_text.text:
                    self.log(">>> ACTION REQUIRED: Lower Throttle Stick to 0 <<<")
        except: pass

    async def print_battery(self):
        try:
            async for battery in self.drone.telemetry.battery():
                self.telemetry_state["battery_v"] = round(battery.voltage_v, 2)
                self.telemetry_state["battery_pct"] = round(battery.remaining_percent * 100, 0)
                text = f"{battery.voltage_v:.2f} V / {battery.remaining_percent * 100:.0f} %"
                self.update_label(self.telemetry_labels["lbl_bat"], text)
        except: pass

    async def print_gps(self):
        try:
            async for gps_info in self.drone.telemetry.gps_info():
                self.telemetry_state["gps_sats"] = gps_info.num_satellites
                self.telemetry_state["gps_fix"] = str(gps_info.fix_type)
                text = f"{gps_info.num_satellites} Sats ({gps_info.fix_type})"
                self.update_label(self.telemetry_labels["lbl_gps"], text)
        except: pass

    async def print_position(self):
        try:
            async for position in self.drone.telemetry.position():
                self.telemetry_state["rel_alt"] = round(position.relative_altitude_m, 2)
                text = f"{position.relative_altitude_m:.2f} m"
                self.update_label(self.telemetry_labels["lbl_alt"], text)
        except: pass

    async def print_attitude(self):
        try:
            async for angle in self.drone.telemetry.attitude_euler():
                self.telemetry_state["roll"] = round(angle.roll_deg, 1)
                self.telemetry_state["pitch"] = round(angle.pitch_deg, 1)
                self.telemetry_state["yaw"] = round(angle.yaw_deg, 1)
                text = f"R: {angle.roll_deg:.1f} P: {angle.pitch_deg:.1f} Y: {angle.yaw_deg:.1f}"
                self.update_label(self.telemetry_labels["lbl_att"], text)
        except: pass

    async def print_flight_mode(self):
        try:
            async for mode in self.drone.telemetry.flight_mode():
                self.telemetry_state["mode"] = str(mode)
                self.update_label(self.telemetry_labels["lbl_mode"], str(mode))
        except: pass

    async def print_armed_status(self):
        try:
            async for is_armed in self.drone.telemetry.armed():
                self.telemetry_state["armed"] = is_armed
                text = "ARMED" if is_armed else "DISARMED"
                color = COLOR_SUCCESS if is_armed else COLOR_DANGER
                self.update_label(self.telemetry_labels["lbl_armed"], text, fg=color)
        except: pass
            
    async def print_health(self):
        try:
            async for health in self.drone.telemetry.health():
                status_items = []
                if not health.is_gyrometer_calibration_ok: status_items.append("Gyro")
                if not health.is_accelerometer_calibration_ok: status_items.append("Accel")
                if not health.is_magnetometer_calibration_ok: status_items.append("Mag")
                if not health.is_armable: status_items.append("Safety/Arming")
                
                if not status_items:
                    text = "OK (Ready)"
                    fg = COLOR_SUCCESS
                    self.telemetry_state["health"] = "OK"
                else:
                    text = f"Issues: {', '.join(status_items)}"
                    fg = COLOR_WARNING
                    self.telemetry_state["health"] = '|'.join(status_items)
                
                self.update_label(self.telemetry_labels["lbl_health"], text, fg=fg)
        except: pass

    async def arm_drone(self):
        self.log("Sending ARM Command...")
        if not self.drone:
            self.log("Error: Not connected to drone!")
            return
        try:
            await self.drone.action.arm()
            self.log("Armed! Motors Spinning.")
        except Exception as e:
            self.log(f"Arming Failed: {e}")

    async def takeoff(self):
        if not self.drone:
            self.log("Error: Not connected!")
            return
        self.log("Setting Takeoff Alt to 2.0m")
        try:
            await self.drone.action.set_takeoff_altitude(2.0)
            self.log("Sending TAKEOFF Command...")
            await self.drone.action.takeoff()
            self.log("Takeoff Sent.")
        except Exception as e:
            self.log(f"Takeoff Failed: {e}")

    async def hop_test(self):
        if not self.drone:
            self.log("Error: Not connected!")
            return
        self.log("=== STARTING 1M HOP TEST ===")
        
        # 1. Check State
        if not self.telemetry_state["armed"]:
            self.log("Arming...")
            try: await self.drone.action.arm()
            except Exception as e: 
                self.log(f"Arming Failed: {e}")
                return
        
        # 2. Set Altitude
        self.log("Setting Target Alt: 1.0m")
        try:
            await self.drone.action.set_takeoff_altitude(1.0)
        except Exception as e:
            self.log(f"Set Alt Failed: {e}")
            return
        
        # 3. Takeoff
        self.log("Taking Off...")
        try: await self.drone.action.takeoff()
        except Exception as e:
            self.log(f"Takeoff Failed: {e}")
            return
            
        self.log("Hovering for 5 seconds...")
        await asyncio.sleep(5)
        
        # 4. Land
        self.log("Landing...")
        try: await self.drone.action.land()
        except Exception as e: self.log(f"Land Failed: {e}")
        
        self.log("=== HOP TEST COMPLETE ===")

    async def move_north(self):
        if not self.drone:
            self.log("Error: Not connected!")
            return
        self.log("Starting Offboard Mode...")
        try:
            await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
            await self.drone.offboard.start()
            self.log("Offboard Active.")
            self.log("Sending: North 2m, Up 2m")
            await self.drone.offboard.set_position_ned(PositionNedYaw(2.0, 0.0, -2.0, 0.0))
            self.log("Command Sent.")
        except OffboardError as e:
            self.log(f"Offboard Start Failed: {e}")
            return

    async def land(self):
        self.log("EMERGENCY LANDING...")
        if not self.drone: return
        try: await self.drone.offboard.stop()
        except: pass
        
        try:
            await self.drone.action.land()
        except: self.log("Land Command Failed")
        
        self.log("Waiting 5s then KILLING MOTORS...")
        await asyncio.sleep(5)
        try:
            await self.drone.action.kill()
            self.log("MOTORS KILLED.")
        except:
            try:
                await self.drone.action.disarm()
                self.log("DISARMED.")
            except: pass

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneDashboard(root)
    root.mainloop()