from pymavlink import mavutil
import time

# Connect to the MAVProxy bridge
master = mavutil.mavlink_connection('udp:127.0.0.1:14540')

for port in range(1, 5):
    print(f"Pulsing PWM Port {port}...")
    # Send MAV_CMD_ACTUATOR_TEST (310)
    master.mav.command_long_send(
        1, 1,                          # target_system, target_component
        310, 0,                        # command, confirmation
        0.1, 2.0, port, 1.0,           # val, timeout, index, motor_function
        0, 0, 0                        # param 5-7 (unused)
    )
    time.sleep(4)
