from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
master.wait_heartbeat()
print("Connected")

# Reset all params
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE,
    0,
    2,  # param reset
    0,0,0,0,0,0
)

print("Reset command sent")
time.sleep(5)

# Reboot
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
    0,
    1,0,0,0,0,0,0
)

print("Reboot sent")
