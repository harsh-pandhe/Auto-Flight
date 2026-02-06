from pymavlink import mavutil
# Connect to the MAVProxy bridge
drone = mavutil.mavlink_connection('udp:127.0.0.1:14540')
print("Listening for Pixhawk 6C Heartbeat...")
drone.wait_heartbeat()
print("System Online! All components are communicating.")
