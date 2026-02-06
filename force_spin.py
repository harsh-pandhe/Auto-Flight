from pymavlink import mavutil
import time

# Connect to the MAVProxy bridge
master = mavutil.mavlink_connection('udp:127.0.0.1:14540')

print("Nudging Motor 1 at 15% throttle... Press Ctrl+C to stop.")
try:
    while True:
        # Command 310: Actuator Test
        # Params: Value=0.15, Timeout=1.0s, Index=1, Function=1 (Motor)
        master.mav.command_long_send(
            1, 1, 310, 0,
            0.15, 1.0, 1.0, 1.0, 0, 0, 0
        )
        time.sleep(0.5) 
except KeyboardInterrupt:
    print("Stopped.")
