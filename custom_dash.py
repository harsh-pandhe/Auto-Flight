import tkinter as tk
from pymavlink import mavutil

# Connect to the UDP stream coming from the Raspberry Pi
print("Waiting for heartbeat...")
master = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
master.wait_heartbeat()
print("Heartbeat received! Dashboard Connected.")

def send_arm():
    print("Commanding ARM...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)

def send_disarm():
    print("Commanding DISARM...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        0, 0, 0, 0, 0, 0, 0)

def send_takeoff():
    print("Commanding TAKEOFF to 1.5 meters...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, 1.5)

# Build the Desktop GUI
app = tk.Tk()
app.title("Project ASCEND - Command Dashboard")
app.geometry("400x300")
app.configure(bg="#2b2b2b")

title_label = tk.Label(app, text="FLIGHT CONTROLS", fg="white", bg="#2b2b2b", font=("Arial", 16, "bold"))
title_label.pack(pady=20)

arm_btn = tk.Button(app, text="ARM DRONE", bg="green", fg="white", font=("Arial", 12, "bold"), width=20, command=send_arm)
arm_btn.pack(pady=10)

takeoff_btn = tk.Button(app, text="TAKEOFF (1.5m)", bg="blue", fg="white", font=("Arial", 12, "bold"), width=20, command=send_takeoff)
takeoff_btn.pack(pady=10)

disarm_btn = tk.Button(app, text="EMERGENCY DISARM", bg="red", fg="white", font=("Arial", 12, "bold"), width=20, command=send_disarm)
disarm_btn.pack(pady=10)

app.mainloop()
