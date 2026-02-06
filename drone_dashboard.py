import tkinter as tk
from tkinter import scrolledtext
import asyncio
import threading
import csv
from datetime import datetime
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

# --- Configuration ---
CONNECTION_STRING = "serial:///dev/ttyUSB0:57600"  # Your Telemetry Radio

class DroneDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCEND Drone Control Center")
        self.root.geometry("800x700") # Increased size for logging UI
        
        self.drone = System()
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
        self.console.insert(tk.END, message + "\n")
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
        lbl_title = tk.Label(self.root, text="Bench Test Dashboard", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # Main Layout: Left for Controls, Right for Telemetry
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10)

        left_col = tk.Frame(main_frame)
        left_col.pack(side=tk.LEFT, fill="y", padx=10)
        
        right_col = tk.Frame(main_frame)
        right_col.pack(side=tk.RIGHT, fill="both", expand=True, padx=10)

        # --- Connection Section (Left) ---
        frame_conn = tk.LabelFrame(left_col, text="Connection", padx=5, pady=5)
        frame_conn.pack(fill="x", pady=5)
        btn_connect = tk.Button(frame_conn, text="1. CONNECT", bg="#DDDDDD", command=lambda: self.run_async(self.connect_drone()))
        btn_connect.pack(fill="x", pady=2)
        
        btn_refresh = tk.Button(frame_conn, text="2. REFRESH STREAMS", bg="#EEEEEE", command=lambda: self.run_async(self.configure_rates()))
        btn_refresh.pack(fill="x", pady=2)

        # --- Logging Section (Left - NEW) ---
        frame_log = tk.LabelFrame(left_col, text="Data Logging", padx=5, pady=5)
        frame_log.pack(fill="x", pady=5)
        
        self.btn_log = tk.Button(frame_log, text="START LOGGING", bg="#DDDDDD", command=self.toggle_logging)
        self.btn_log.pack(fill="x", pady=2)

        # --- Flight Controls (Left) ---
        frame_flight = tk.LabelFrame(left_col, text="Controls (Props OFF!)", padx=5, pady=5)
        frame_flight.pack(fill="x", pady=10)

        btn_arm = tk.Button(frame_flight, text="3. ARM", bg="orange", fg="black", command=lambda: self.run_async(self.arm_drone()))
        btn_arm.pack(fill="x", pady=2)

        btn_takeoff = tk.Button(frame_flight, text="4. FAKE TAKEOFF (2.0m)", bg="green", fg="white", command=lambda: self.run_async(self.takeoff()))
        btn_takeoff.pack(fill="x", pady=2)

        btn_move = tk.Button(frame_flight, text="5. MOVE NORTH", bg="blue", fg="white", command=lambda: self.run_async(self.move_north()))
        btn_move.pack(fill="x", pady=2)

        btn_land = tk.Button(frame_flight, text="6. LAND & KILL", bg="red", fg="white", command=lambda: self.run_async(self.land()))
        btn_land.pack(fill="x", pady=2)

        # --- Telemetry Section (Right) ---
        frame_telemetry = tk.LabelFrame(right_col, text="Live Telemetry", padx=10, pady=10)
        frame_telemetry.pack(fill="x", pady=5)

        # Grid for telemetry data
        self.lbl_bat = tk.Label(frame_telemetry, text="Battery: -- V / -- %", font=("Consolas", 12))
        self.lbl_bat.grid(row=0, column=0, sticky="w", padx=5, pady=2)

        self.lbl_gps = tk.Label(frame_telemetry, text="GPS: -- Satellites (Fix: --)", font=("Consolas", 12))
        self.lbl_gps.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.lbl_alt = tk.Label(frame_telemetry, text="Rel Alt: -- m", font=("Consolas", 12))
        self.lbl_alt.grid(row=2, column=0, sticky="w", padx=5, pady=2)

        self.lbl_att = tk.Label(frame_telemetry, text="Attitude: R: -- P: -- Y: --", font=("Consolas", 12))
        self.lbl_att.grid(row=3, column=0, sticky="w", padx=5, pady=2)

        self.lbl_mode = tk.Label(frame_telemetry, text="Mode: --", font=("Consolas", 12, "bold"))
        self.lbl_mode.grid(row=4, column=0, sticky="w", padx=5, pady=2)

        self.lbl_armed = tk.Label(frame_telemetry, text="State: DISARMED", font=("Consolas", 12, "bold"), fg="red")
        self.lbl_armed.grid(row=5, column=0, sticky="w", padx=5, pady=2)

        self.lbl_health = tk.Label(frame_telemetry, text="Health: Checking...", font=("Consolas", 10), fg="gray")
        self.lbl_health.grid(row=6, column=0, sticky="w", padx=5, pady=2)
        
        # --- Console Output (Bottom Right) ---
        self.console = scrolledtext.ScrolledText(right_col, height=15, state='disabled', bg="black", fg="#00FF00", font=("Consolas", 10))
        self.console.pack(padx=5, pady=5, fill="both", expand=True)

    # --- Logging Functions ---
    def toggle_logging(self):
        if not self.logging_active:
            self.start_logging()
            self.btn_log.config(text="STOP LOGGING", bg="#FFCCCC")
        else:
            self.stop_logging()
            self.btn_log.config(text="START LOGGING", bg="#DDDDDD")

    def start_logging(self):
        filename = f"telemetry_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            self.csv_file = open(filename, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            # Write Header
            self.csv_writer.writerow(["Timestamp", "Battery_V", "Battery_Pct", "GPS_Sats", "GPS_Fix", "Rel_Alt", "Roll", "Pitch", "Yaw", "Mode", "Armed", "Health"])
            self.logging_active = True
            self.log(f"-- LOGGING STARTED: {filename}")
            # Start background logging task
            self.run_async(self.logging_loop())
        except Exception as e:
            self.log(f"-- Log Start Failed: {e}")

    def stop_logging(self):
        self.logging_active = False
        if self.csv_file:
            self.csv_file.close()
            self.csv_file = None
        self.log("-- LOGGING STOPPED.")

    async def logging_loop(self):
        """Writes current telemetry state to CSV at 10Hz"""
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
            await asyncio.sleep(0.1) # 10 Hz

    # --- Async Logic Functions ---

    async def connect_drone(self):
        self.log(f"-- Connecting to {CONNECTION_STRING}...")
        await self.drone.connect(system_address=CONNECTION_STRING)
        
        self.log("-- Waiting for heartbeat...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.log("-- SUCCESS: Connected to Drone!")
                # Start telemetry tasks
                self.run_async(self.telemetry_loop())
                break
    
    async def telemetry_loop(self):
        """Start all telemetry listeners"""
        self.log("-- Starting Telemetry Listeners...")
        
        # Start listeners immediately (don't wait for rate configuration)
        asyncio.create_task(self.print_battery())
        asyncio.create_task(self.print_gps())
        asyncio.create_task(self.print_position())
        asyncio.create_task(self.print_attitude())
        asyncio.create_task(self.print_flight_mode())
        asyncio.create_task(self.print_armed_status())
        asyncio.create_task(self.print_status_text())
        asyncio.create_task(self.print_health())
        
        # Attempt to set rates in background
        asyncio.create_task(self.configure_rates())

    async def configure_rates(self):
        self.log("-- Sending Rate Configuration Commands...")
        try:
            await self.drone.telemetry.set_rate_battery(1.0)
            await self.drone.telemetry.set_rate_gps_info(2.0)
            await self.drone.telemetry.set_rate_position(5.0)
            await self.drone.telemetry.set_rate_attitude(10.0)
            self.log("-- Rate Configuration Sent.")
        except Exception as e:
            self.log(f"-- Rate Config Warning: {e}")

    async def print_status_text(self):
        """Listen for status text (Errors/Warnings) from the drone"""
        try:
            async for status_text in self.drone.telemetry.status_text():
                self.log(f"DRONE: {status_text.text}")
        except Exception as e:
            self.log(f"Status Stream Error: {e}")

    async def print_battery(self):
        try:
            async for battery in self.drone.telemetry.battery():
                # Save Data
                self.telemetry_state["battery_v"] = round(battery.voltage_v, 2)
                self.telemetry_state["battery_pct"] = round(battery.remaining_percent * 100, 0)
                
                # Update UI
                text = f"Battery: {battery.voltage_v:.2f} V / {battery.remaining_percent * 100:.0f} %"
                self.update_label(self.lbl_bat, text)
        except Exception as e:
            self.log(f"Battery Stream Error: {e}")

    async def print_gps(self):
        try:
            async for gps_info in self.drone.telemetry.gps_info():
                # Save Data
                self.telemetry_state["gps_sats"] = gps_info.num_satellites
                self.telemetry_state["gps_fix"] = str(gps_info.fix_type)

                # Update UI
                text = f"GPS: {gps_info.num_satellites} Sats (Fix: {gps_info.fix_type})"
                self.update_label(self.lbl_gps, text)
        except Exception as e:
            self.log(f"GPS Stream Error: {e}")

    async def print_position(self):
        try:
            async for position in self.drone.telemetry.position():
                # Save Data
                self.telemetry_state["rel_alt"] = round(position.relative_altitude_m, 2)

                # Update UI
                text = f"Rel Alt: {position.relative_altitude_m:.2f} m"
                self.update_label(self.lbl_alt, text)
        except Exception as e:
            self.log(f"Position Stream Error: {e}")

    async def print_attitude(self):
        try:
            async for angle in self.drone.telemetry.attitude_euler():
                # Save Data
                self.telemetry_state["roll"] = round(angle.roll_deg, 1)
                self.telemetry_state["pitch"] = round(angle.pitch_deg, 1)
                self.telemetry_state["yaw"] = round(angle.yaw_deg, 1)

                # Update UI
                text = f"Attitude: R: {angle.roll_deg:.1f} P: {angle.pitch_deg:.1f} Y: {angle.yaw_deg:.1f}"
                self.update_label(self.lbl_att, text)
        except Exception as e:
            self.log(f"Attitude Stream Error: {e}")

    async def print_flight_mode(self):
        try:
            async for mode in self.drone.telemetry.flight_mode():
                # Save Data
                self.telemetry_state["mode"] = str(mode)

                # Update UI
                text = f"Mode: {mode}"
                self.update_label(self.lbl_mode, text)
        except Exception as e:
            self.log(f"Mode Stream Error: {e}")

    async def print_armed_status(self):
        try:
            async for is_armed in self.drone.telemetry.armed():
                # Save Data
                self.telemetry_state["armed"] = is_armed

                # Update UI
                text = "State: ARMED" if is_armed else "State: DISARMED"
                color = "green" if is_armed else "red"
                self.update_label(self.lbl_armed, text, fg=color)
        except Exception as e:
            self.log(f"Armed Stream Error: {e}")
            
    async def print_health(self):
        try:
            async for health in self.drone.telemetry.health():
                status_items = []
                if not health.is_gyrometer_calibration_ok: status_items.append("Gyro Fail")
                if not health.is_accelerometer_calibration_ok: status_items.append("Accel Fail")
                if not health.is_magnetometer_calibration_ok: status_items.append("Mag Fail")
                if not health.is_armable: status_items.append("Not Armable")
                
                if not status_items:
                    text = "Health: OK (Ready to Fly)"
                    fg = "green"
                    self.telemetry_state["health"] = "OK"
                else:
                    text = f"Health Issue: {', '.join(status_items)}"
                    fg = "orange"
                    self.telemetry_state["health"] = '|'.join(status_items)
                
                self.update_label(self.lbl_health, text, fg)
        except Exception as e:
            self.log(f"Health Stream Error: {e}")

    async def arm_drone(self):
        self.log("-- Sending ARM Command...")
        try:
            await self.drone.action.arm()
            self.log("-- Armed! (Motors should spin idle)")
        except Exception as e:
            self.log(f"-- Arming Failed: {e}")

    async def takeoff(self):
        self.log("-- Setting Takeoff Alt to 2.0m")
        await self.drone.action.set_takeoff_altitude(2.0)
        self.log("-- Sending TAKEOFF Command...")
        try:
            await self.drone.action.takeoff()
            self.log("-- Takeoff Sent. Motors should ramp up.")
        except Exception as e:
            self.log(f"-- Takeoff Failed: {e}")

    async def move_north(self):
        self.log("-- Starting Offboard Mode...")
        # Send initial setpoint
        await self.drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
        
        try:
            await self.drone.offboard.start()
            self.log("-- Offboard Active.")
        except OffboardError as e:
            self.log(f"-- Offboard Start Failed: {e}")
            return

        self.log("-- Sending: North 2m, Up 2m")
        await self.drone.offboard.set_position_ned(PositionNedYaw(2.0, 0.0, -2.0, 0.0))
        self.log("-- Command Sent. Listen for pitch change.")

    async def land(self):
        self.log("-- Landing...")
        try:
            await self.drone.offboard.stop()
        except:
            pass
        await self.drone.action.land()
        
        self.log("-- Waiting 5s then FORCE DISARMING...")
        await asyncio.sleep(5)
        try:
            await self.drone.action.kill()
            self.log("-- KILLED.")
        except:
            await self.drone.action.disarm()
            self.log("-- Disarmed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DroneDashboard(root)
    root.mainloop()