#!/bin/bash
# Livox + ROS 2 Quick Setup
# 
# USAGE: source ./livox_ros2.sh
#
# This script:
# 1. Starts the Livox ROS 2 driver in background
# 2. Configures ROS 2 environment in YOUR current shell
# 3. Returns control to terminal with ros2 commands available

# Only allow sourcing (not direct execution)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "⚠️  Error: This script must be SOURCE'd, not executed!"
    echo ""
    echo "Correct usage:"
    echo "  source ./livox_ros2.sh"
    echo ""
    echo "Wrong usage:"
    echo "  ./livox_ros2.sh"
    echo "  bash ./livox_ros2.sh"
    echo ""
    exit 127
fi

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 (Data Streaming)                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if ROS 2 rolling exists
if [ ! -f /opt/ros/rolling/setup.bash ]; then
    echo "❌ ROS 2 rolling not found!"
    return 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting ROS 2 Livox driver in background..."

# Start driver in isolated background subprocess
(
    unset ROS_DISTRO COLCON_PREFIX_PATH
    source /opt/ros/rolling/setup.bash > /dev/null 2>&1
    source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
    
    # Remove humble paths to prevent library conflicts
    export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    
    ~/ros2_livox_ws/install/livox_ros2_python_driver/bin/livox_driver_node
) &>/dev/null &

# Give driver time to initialize
sleep 2

# Configure ROS 2 environment in THIS shell (will persist for user)
unset ROS_DISTRO COLCON_PREFIX_PATH
source /opt/ros/rolling/setup.bash > /dev/null 2>&1
source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1

# Remove humble paths to prevent library conflicts
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')

echo "✓ Driver listening on UDP port 56301"
echo "✓ Publishing PointCloud2 to: /livox/lidar"
echo "✓ ROS 2 environment ACTIVE in this shell (persistent)"
echo ""
echo "Ready for ROS 2 commands. Try:"
echo "  ros2 topic list              # List all topics"
echo "  ros2 topic echo /livox/lidar  # Stream point cloud data"
echo "  ros2 bag record /livox/lidar  # Record to bag file"
echo ""
echo "In another terminal:"
echo "  source ~/Desktop/GitHub/auto-flight/livox_ros2.sh"
echo "  ros2 topic echo /livox/lidar  # View data from second shell"
echo ""
