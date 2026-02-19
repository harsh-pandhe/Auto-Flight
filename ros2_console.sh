#!/bin/bash
# ROS 2 Livox Data Console
# Use this in a separate terminal to monitor /livox/lidar topic

# Clean environment
unset ROS_DISTRO COLCON_PREFIX_PATH

# Source ROS 2 from absolute paths
source /opt/ros/rolling/setup.bash 2>/dev/null
source /home/iic/ros2_livox_ws/install/setup.bash 2>/dev/null

# Filter out humble paths to prevent conflicts
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         ROS 2 Livox Data Monitor                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Available topics:"
ros2 topic list 2>/dev/null | grep -i livox || echo "No Livox topics found - make sure driver is running"
echo ""
echo "Streaming point cloud data from /livox/lidar..."
echo "Press Ctrl+C to stop"
echo ""

ros2 topic echo /livox/lidar
