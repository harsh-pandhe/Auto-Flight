import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

async def run():
    # 1. SETUP: Connect to the Pixhawk
    drone = System()
    
    # UPDATED FOR PC TELEMETRY RADIO:
    # Uses /dev/ttyUSB0 (from your screenshot) and 57600 baud (standard for Telemetry radios)
    print("-- Connecting to drone on /dev/ttyUSB0...")
    await drone.connect(system_address="serial:///dev/ttyUSB0:57600")

    print("-- Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    # 2. PRE-FLIGHT CHECKS: Wait for GPS (Required for Auto modes)
    print("-- Waiting for Global Position Estimate (Green LED)...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    # 3. ARMING
    print("-- Arming")
    try:
        await drone.action.arm()
    except Exception as e:
        print(f"Arming failed: {e}")
        return

    # 4. TASK 1: TAKEOFF (Logic Check)
    print("-- Taking off (Logic Check)")
    await drone.action.set_takeoff_altitude(2.0) # Set target height 2m
    await drone.action.takeoff()
    
    # Wait 10 seconds. 
    # OBSERVE: Motors should spin up to "Hover Throttle" (approx 40-50% speed)
    await asyncio.sleep(10)

    # 5. TASK 2: OFFBOARD CONTROL (Simulated Movement)
    print("-- Starting Offboard Mode")
    
    # Send a setpoint BEFORE starting offboard mode (Safety requirement)
    # 0,0,0 = Hold current position
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming due to error")
        await drone.action.disarm()
        return

    # COMMAND: Move 2 meters North, 2 meters UP (Negative Z)
    print("-- Moving North 2m, Up 2m")
    # North (x), East (y), Down (z), Yaw (deg)
    await drone.offboard.set_position_ned(PositionNedYaw(2.0, 0.0, -2.0, 0.0))
    
    # Wait 5 seconds.
    # OBSERVE: Rear motors should spin faster (to pitch nose down/forward)
    await asyncio.sleep(5)

    # 6. TASK 3: LANDING
    print("-- Landing")
    try:
        await drone.offboard.stop() # Stop Offboard control
    except:
        pass # If it fails, we overwrite with Action Land anyway
        
    await drone.action.land()
    
    # Wait for disarm
    async for is_armed in drone.telemetry.armed():
        if not is_armed:
            print("-- Disarm detected. Mission Complete.")
            break

if __name__ == "__main__":
    asyncio.run(run())
