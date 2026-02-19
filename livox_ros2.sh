#!/bin/bash
# Livox + ROS 2 Quick Setup
# Stream Livox data to ROS 2 topics (no GUI)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 (Data Streaming)                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Find ROS 2 (need rolling for ros2 CLI, but clean environment to avoid mixing)
if [ -f /opt/ros/rolling/setup.bash ]; then
    ROS_SETUP="/opt/ros/rolling/setup.bash"
else
    echo "❌ ROS 2 rolling not found!"
    exit 1
fi

echo "Starting ROS 2 Livox driver..."
# Note: SDK quick_start is not needed - the driver itself binds to port 56301
exec bash << 'SHELL'
# Completely isolate ROS 2 rolling from humble
# Unset everything first
unset ROS_DISTRO COLCON_PREFIX_PATH

# Source rolling and capture its environment
source /opt/ros/rolling/setup.bash > /dev/null 2>&1
source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1

# Now explicitly remove any humble paths from LD_LIBRARY_PATH and PYTHONPATH
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')

echo "✓ ROS 2 environment ready"
echo "Driver listening on UDP port 56301"
echo "Driver publishing PointCloud2 to: /livox/lidar"
echo ""
echo "In another terminal, run:"
echo "  source /opt/ros/rolling/setup.bash"
echo "  source ~/ros2_livox_ws/install/setup.bash"
echo "  ros2 topic echo /livox/lidar"
echo ""

~/ros2_livox_ws/install/livox_ros2_python_driver/bin/livox_driver_node
SHELL
