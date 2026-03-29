from pymavlink import mavutil
import time

master = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)
master.wait_heartbeat()
print("Connected")

def set_param(name, value, ptype):
    master.mav.param_set_send(
        master.target_system,
        master.target_component,
        name.encode('utf-8'),
        float(value),
        ptype
    )
    time.sleep(0.3)

# Required params
params = [
    ("CBRK_IO_SAFETY", 22027, mavutil.mavlink.MAV_PARAM_TYPE_REAL32),
    ("COM_ARM_WO_GPS", 1, mavutil.mavlink.MAV_PARAM_TYPE_INT32),
    ("SYS_HAS_GPS", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32),
    ("SYS_HAS_MAG", 0, mavutil.mavlink.MAV_PARAM_TYPE_INT32),
    ("EKF2_MAG_TYPE", 5, mavutil.mavlink.MAV_PARAM_TYPE_INT32),
    ("PWM_MAIN_FUNC1", 101, mavutil.mavlink.MAV_PARAM_TYPE_INT32),
]

for p in params:
    print("Setting", p[0])
    set_param(*p)

# Save params
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_PREFLIGHT_STORAGE,
    0,
    1,  # save
    0,0,0,0,0,0
)

print("Save sent")

time.sleep(2)

# Reboot
master.mav.command_long_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN,
    0,
    1,0,0,0,0,0,0
)
