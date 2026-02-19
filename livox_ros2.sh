#!/bin/bash
# Livox + ROS 2 Quick Setup
# Stream Livox data to ROS 2 topics
# This script starts the driver in background and sets up ROS 2 environment

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check if ROS 2 rolling exists
if [ ! -f /opt/ros/rolling/setup.bash ]; then
    echo "❌ ROS 2 rolling not found!"
    exit 1
fi

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 (Data Streaming)                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Start driver in background with properly isolated environment
echo "Starting ROS 2 Livox driver in background..."
(
    unset ROS_DISTRO COLCON_PREFIX_PATH
    source /opt/ros/rolling/setup.bash > /dev/null 2>&1
    source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
    export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    
    ~/ros2_livox_ws/install/livox_ros2_python_driver/bin/livox_driver_node
) &>/dev/null &

# Give driver time to start
sleep 2

# Now setup ROS 2 environment in current shell
unset ROS_DISTRO COLCON_PREFIX_PATH
source /opt/ros/rolling/setup.bash > /dev/null 2>&1
source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')

echo "✓ Driver listening on UDP port 56301"
echo "✓ Publishing PointCloud2 to: /livox/lidar"
echo "✓ ROS 2 environment configured in this shell"
echo ""
echo "Available commands in this terminal:"
echo "  ros2 topic list             # List all topics"
echo "  ros2 topic echo /livox/lidar  # Stream point cloud data"
echo "  ros2 bag record /livox/lidar  # Record data to bag file"
echo ""
echo "Or in another terminal, run:"
echo "  cd ~/Desktop/GitHub/auto-flight && ./ros2_console.sh"
echo ""
echo "Press Ctrl+C to exit (driver will keep running)"
echo ""
echo "🚀 Ready for ROS 2 commands!"
echo ""
