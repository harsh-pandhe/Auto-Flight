#!/bin/bash
# Quick Reference - Livox Mid 360 Integration
# Copy-paste commands for common tasks

# ============================================
# QUICK START
# ============================================

# Start Open3D visualization (easiest)
cd ~/Desktop/GitHub/auto-flight
./livox.sh
# Select: 1

# Start ROS 2 driver with environment ready
cd ~/Desktop/GitHub/auto-flight
./livox_ros2.sh

# Then in same terminal, try:
ros2 topic list
ros2 topic echo /livox/lidar

# ============================================
# ROS 2 COMMANDS
# ============================================

# Source ROS 2 environment (if needed)
source /opt/ros/rolling/setup.bash
source ~/ros2_livox_ws/install/setup.bash

# List all topics
ros2 topic list

# Show only Livox topics
ros2 topic list | grep livox

# Stream point cloud data (limited output)
timeout 5 ros2 topic echo /livox/lidar | head -50

# Record to bag file (Ctrl+C to stop)
ros2 bag record /livox/lidar -o flight_data_001

# Play back bag file
ros2 bag play flight_data_001

# Stream at reduced rate (every 5th message)
ros2 topic echo /livox/lidar --rate 2.0

# Get topic info
ros2 topic info /livox/lidar

# View message definition
ros2 interface show sensor_msgs/msg/PointCloud2

# ============================================
# MONITORING & DEBUGGING
# ============================================

# Check if driver is running
ps aux | grep livox_driver_node | grep -v grep

# View driver logs (if running in background)
tail -50 /tmp/livox_driver.log

# Start packet sniffer (via menu)
cd ~/Desktop/GitHub/auto-flight
./livox.sh
# Select: 3

# Check if Livox hardware is reachable
ping 192.168.1.199

# Check network interface
ip addr show enp130s0
ss -tlnup | grep 56301

# ============================================
# CLEANUP
# ============================================

# Kill all Livox processes
pkill -9 -f "livox"

# Kill all Python processes (careful!)
pkill -9 -f "python3"

# ============================================
# FILE LOCATIONS
# ============================================

# Main scripts
~/Desktop/GitHub/auto-flight/livox.sh                 # Main menu
~/Desktop/GitHub/auto-flight/livox_ros2.sh           # ROS 2 driver launcher
~/Desktop/GitHub/auto-flight/ros2_console.sh         # ROS 2 data monitor
~/Desktop/GitHub/auto-flight/livox_launcher.sh       # Open3D launcher

# Source code
~/Desktop/GitHub/auto-flight/livox_3d_mapper.py      # Open3D visualization
~/Desktop/GitHub/auto-flight/livox_packet_sniffer.py # UDP debugger

# ROS 2 workspace
~/ros2_livox_ws/                                      # ROS 2 workspace root
~/ros2_livox_ws/src/livox_ros2_python_driver/        # Driver source
~/ros2_livox_ws/install/livox_ros2_python_driver/    # Compiled driver

# SDK
~/Desktop/GitHub/auto-flight/Livox-SDK2/             # Vendor SDK source
~/Desktop/GitHub/auto-flight/Livox-SDK2/build/       # Compiled binaries

# ============================================
# CONFIGURATION
# ============================================

# Livox hardware
IP Address:    192.168.1.199
UDP Port:      56301
Data Rate:     10 Hz
Points/Frame:  96 Cartesian points (XYZ)

# PC Network
IP Address:    192.168.1.10
Netmask:       255.255.255.0
Interface:     enp130s0
Config:        Static IP (not DHCP)

# ROS 2
Distribution: rolling (/opt/ros/rolling)
Python:       3.12
PointCloud2 Topic: /livox/lidar
Frame ID:     livox_frame

# ============================================
# TROUBLESHOOTING
# ============================================

# Issue: "Command not found: ros2"
Fix: Source ROS 2 environment first
source /opt/ros/rolling/setup.bash
source ~/ros2_livox_ws/install/setup.bash

# Issue: "Address already in use" on port 56301
Fix: Kill existing processes
pkill -9 -f "livox"
sleep 2
./livox.sh

# Issue: No point cloud data
Check:
1. Is driver running? (ps aux | grep livox_driver_node)
2. Is hardware powered on?
3. Is network cable connected?
4. Run packet sniffer to verify UDP arrival

# Issue: Network not configured
Reconfigure static IP:
sudo ip addr add 192.168.1.10/24 dev enp130s0
sudo ip route add default via 192.168.1.1

# ============================================
# USEFUL LINKS
# ============================================

ROS 2 Documentation:     https://docs.ros.org/en/rolling/
Livox SDK Documentation: https://github.com/Livox-SDK/Livox-SDK2
PointCloud2 Format:      http://docs.ros.org/humble/p/sensor_msgs/

# ============================================
# NOTES
# ============================================

- Default visualization is Open3D (most reliable)
- ROS 2 integration available for robotics applications
- All code is on GitHub at: https://github.com/harsh-pandhe/Auto-Flight
- Last tested: February 19, 2026
- Status: Production Ready ✅

