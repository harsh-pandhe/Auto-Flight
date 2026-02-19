#!/bin/bash
# Livox + ROS 2 Quick Setup
# Stream Livox data to ROS 2 topics (no GUI)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 (Data Streaming)                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Find ROS 2
if [ -f /opt/ros/rolling/setup.bash ]; then
    ROS_SETUP="/opt/ros/rolling/setup.bash"
elif [ -f /opt/ros/humble/setup.bash ]; then
    ROS_SETUP="/opt/ros/humble/setup.bash"
else
    echo "❌ ROS 2 not found!"
    exit 1
fi

echo "Starting Livox SDK..."
./Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start \
    ./Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json > /tmp/sdk.log 2>&1 &
SDK_PID=$!
sleep 3

echo "Starting ROS 2 Livox driver..."
exec bash << 'SHELL'
# Clean environment
unset PYTHONPATH PYTHONHOME
source /opt/ros/rolling/setup.bash 2>/dev/null || source /opt/ros/humble/setup.bash
source ~/ros2_livox_ws/install/setup.bash

# Run driver in foreground
echo "✓ ROS 2 environment ready"
echo "Driver publishing to: /livox/lidar (PointCloud2)"
echo ""
echo "In another terminal, you can:"
echo "  ros2 topic list"
echo "  ros2 topic echo /livox/lidar"
echo "  rviz2 -d ~/Desktop/GitHub/auto-flight/livox_rviz_config.rviz"
echo ""

ros2 run livox_ros2_python_driver livox_driver_node
SHELL
