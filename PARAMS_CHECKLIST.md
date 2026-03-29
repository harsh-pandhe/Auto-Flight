# ISRO 1M Satellite Parameters Checklist

## Flight Control Parameters

### Basic Flight Parameters
- [ ] Vehicle type (MAV_TYPE)
- [ ] Autopilot type (MAV_AUTOPILOT)
- [ ] Flight mode (MAV_MODE)
- [ ] System status (MAV_STATE)

### Navigation Parameters
- [ ] Waypoint count
- [ ] Current waypoint index
- [ ] Navigation mode (AUTO, GUIDED, RTL)
- [ ] GPS fix status
- [ ] Altitude above home
- [ ] Ground speed
- [ ] Airspeed

### Telemetry Parameters
- [ ] Battery voltage
- [ ] Battery current
- [ ] Battery remaining percentage
- [ ] Signal strength (RSSI)
- [ ] Flight time
- [ ] Temperature
- [ ] Pressure

### System Parameters
- [ ] System ID
- [ ] Component ID
- [ ] Heartbeat interval
- [ ] Connection status
- [ ] Error count
- [ ] Reset count

## MAVLink Strict Lock Parameters

### Lock Status
- [ ] Lock acquired timestamp
- [ ] Lock timeout duration
- [ ] Lock state (locked/unlocked)
- [ ] Last heartbeat timestamp

### Communication Parameters
- [ ] Baud rate
- [ ] Serial port
- [ ] Connection timeout
- [ ] Message rate
- [ ] Retry attempts

## Safety Parameters

### Emergency Procedures
- [ ] Emergency landing altitude
- [ ] Return to launch altitude
- [ ] Minimum safe altitude
- [ ] Emergency stop command
- [ ] Auto-recovery procedures

### Threshold Values
- [ ] Battery low warning threshold
- [ ] Battery critical threshold
- [ ] Signal loss timeout
- [ ] Altitude limit
- [ ] Speed limit
- [ ] Temperature limit

## Mission Parameters

### Mission Planning
- [ ] Mission waypoints
- [ ] Mission duration
- [ ] Mission type (waypoint, survey, etc.)
- [ ] Waypoint altitude
- [ ] Waypoint speed
- [ ] Waypoint heading

### Mission Execution
- [ ] Mission start time
- [ ] Mission completion time
- [ ] Waypoint execution status
- [ ] Mission progress percentage
- [ ] Mission error count