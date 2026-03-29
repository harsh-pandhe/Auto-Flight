# ROS 2 Livox LiDAR Integration

## Overview
This document describes the ROS 2 integration for the Livox Mid 360 LiDAR on Ubuntu 24.04 with ROS 2 Humble.

## Current Status

### ✅ Completed
- **Python Mapper**: Working 3D point cloud visualization using Open3D
  - Parses Livox SDK2 UDP Ethernet packets
  - Renders real-time point cloud with height-based coloring
  - Located: `scripts/python/livox_3d_mapper.py`
  
- **Hardware Connection**: Stable UDP communication
  - Livox at IP: 192.168.1.199
  - UDP Port: 56301 (Livox Mid-360 point cloud stream)
  - PC: Static IP 192.168.1.10 on Ethernet interface
  
- **ROS 2 Infrastructure**: Basic setup complete
  - ROS 2 Humble installed via apt
  - Workspace created: `~/ros2_livox_ws`
  - Python ROS 2 driver package created: `livox_ros2_python_driver`
  - Successfully builds with colcon

### ⚠️ Limitations (ROS 2 Humble vs Official Driver)

The official `livox_ros_driver2` C++ driver is designed for ROS 2 Rolling/Jazzy and has compatibility issues with Humble:

1. **Missing `rclcpp_components`** - Not available in Humble distribution
2. **CMake Interface Issues** - Custom message generation has targeting problems
3. **Python Version Mismatch** - Built with Python 3.10, requires specific environment setup

**Workaround**: Created simpler Python-based ROS 2 driver that works with Humble

## Python ROS 2 Driver

### Location
`~/ros2_livox_ws/src/livox_ros2_python_driver`

### Features
- Receives UDP packets from Livox at 192.168.1.199:56301
- Parses Cartesian coordinate data (both high and low resolution formats)
- Publishes as `sensor_msgs/PointCloud2` on topic `/livox/lidar`
- Real-time point cloud streaming to ROS 2 ecosystem

### Publishing Topic
```
/livox/lidar  (sensor_msgs::PointCloud2)
  - frame_id: "livox_frame"
  - fields: x, y, z (float32), intensity (uint8)
  - 1-to-1 mapping with UDP packet rates
```

### Entry Point
```bash
ros2 run livox_ros2_python_driver livox_driver_node
```

## Building

### Prerequisites
```bash
# Install ROS 2 Humble
curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/ros2.list
sudo apt update
sudo apt install ros-humble-desktop

# Install empy (required for ROS 2 builds)
sudo pip install empy --target=/usr/local/lib/python3.10/dist-packages
```

### Build Steps
```bash
cd ~/ros2_livox_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
```

## Running the Driver

### Option 1: Direct ROS 2 Launch (when rclpy available)
```bash
source /opt/ros/humble/setup.bash
source ~/ros2_livox_ws/install/setup.bash
ros2 run livox_ros2_python_driver livox_driver_node
```

### Option 2: Python 3D Visualization (Current Working Method)
```bash
cd ~/Desktop/GitHub/auto-flight
source venv/bin/activate
python3 scripts/python/livox_3d_mapper.py
```

## Network Configuration

### PC Interface Setup
```bash
# Static IP on Ethernet (already configured)
ip addr show enp130s0
# Result: 192.168.1.10/24

# Verify connectivity
ping 192.168.1.199  # Livox
```

### Firewall Rules
```bash
# Allow UDP port 56301 (if iptables configured)
sudo iptables -A INPUT -p udp --dport 56301 -j ACCEPT
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'em'"
**Solution**: Install empy in system Python site-packages
```bash
sudo pip install empy --target=/usr/local/lib/python3.10/dist-packages
```

### Issue: Livox not sending data
**Solution**: Run Livox SDK2 quick-start to establish connection
```bash
cd ~/Desktop/GitHub/auto-flight/Livox-SDK2/build
./samples/livox_lidar_quick_start/livox_lidar_quick_start
```

### Issue: No UDP packets received
**Solution**: Verify network configuration
```bash
# Sniffer tool to check packet arrival
python3 scripts/python/livox_packet_sniffer.py
```

## Future Integration

### SLAM Integration (Optional)
- LIO-SAM: Light-weight SLAM for LiDAR + IMU
- FAST-LIO2: Fast LiDAR-Inertial Odometry and Mapping
- Both compatible with ROS 2 point cloud input

### Recording
```bash
# Record point cloud stream to ROS bag
ros2 bag record /livox/lidar
```

### Visualization
```bash
# View point cloud in RViz2
rviz2 &
# Add PointCloud2 display, set topic to /livox/lidar
```

## References
- Livox SDK2: https://github.com/Livox-SDK/Livox-SDK2
- Livox ROS2 Driver: https://github.com/Livox-SDK/livox_ros_driver2
- ROS 2 Humble Docs: https://docs.ros.org/en/humble/

## Notes
- The venv was temporarily removed during ROS 2 build troubleshooting; it has been recreated
- empy 4.2.1 installed (note: bloom expects <4, but colcon compatible)
- CMake Python discovery was overridden by removing venv during colcon build
