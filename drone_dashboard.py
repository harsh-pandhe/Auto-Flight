import tkinter as tk
from tkinter import scrolledtext
import asyncio
import threading
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

# --- Configuration ---
CONNECTION_STRING = "serial:///dev/ttyUSB0:57600"  # Your Telemetry Radio

class DroneDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ASCEND Drone Control Center")
        self.root.geometry("600x500")
        
        self.drone = System()
        self.loop = asyncio.new_event_loop()
        
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

    def setup_ui(self):
        # Header
        lbl_title = tk.Label(self.root, text="Bench Test Dashboard", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # Connection Section
        frame_conn = tk.Frame(self.root)
        frame_conn.pack(pady=5)
        btn_connect = tk.Button(frame_conn, text="1. CONNECT", bg="#DDDDDD", command=lambda: self.run_async(self.connect_drone()))
        btn_connect.pack(side=tk.LEFT, padx=5)
        
        btn_gps = tk.Button(frame_conn, text="2. CHECK GPS", bg="#DDDDDD", command=lambda: self.run_async(self.check_gps()))
        btn_gps.pack(side=tk.LEFT, padx=5)

        # Flight Controls
        frame_flight = tk.LabelFrame(self.root, text="Flight Controls (Props OFF!)", padx=10, pady=10)
        frame_flight.pack(pady=10, fill="x", padx=20)

        btn_arm = tk.Button(frame_flight, text="3. ARM", bg="orange", fg="black", command=lambda: self.run_async(self.arm_drone()))
        btn_arm.pack(fill="x", pady=2)

        btn_takeoff = tk.Button(frame_flight, text="4. FAKE TAKEOFF (2.0m)", bg="green", fg="white", command=lambda: self.run_async(self.takeoff()))
        btn_takeoff.pack(fill="x", pady=2)

        btn_move = tk.Button(frame_flight, text="5. MOVE NORTH (Offboard)", bg="blue", fg="white", command=lambda: self.run_async(self.move_north()))
        btn_move.pack(fill="x", pady=2)

        btn_land = tk.Button(frame_flight, text="6. LAND & KILL", bg="red", fg="white", command=lambda: self.run_async(self.land()))
        btn_land.pack(fill="x", pady=2)

        # Console Output
        self.console = scrolledtext.ScrolledText(self.root, height=15, state='disabled', bg="black", fg="#00FF00", font=("Consolas", 10))
        self.console.pack(padx=10, pady=10, fill="both", expand=True)

    # --- Async Logic Functions ---

    async def connect_drone(self):
        self.log(f"-- Connecting to {CONNECTION_STRING}...")
        await self.drone.connect(system_address=CONNECTION_STRING)
        
        self.log("-- Waiting for heartbeat...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                self.log("-- SUCCESS: Connected to Drone!")
                break

    async def check_gps(self):
        self.log("-- Checking GPS Health...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok:
                self.log("-- GPS OK: Green LED Detected.")
            else:
                self.log("-- WARNING: No GPS Lock. Move near window.")
            break

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
