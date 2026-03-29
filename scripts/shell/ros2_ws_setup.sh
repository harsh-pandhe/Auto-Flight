#!/bin/bash
# ROS 2 Livox workspace setup

set -e

ROS2_WS="$HOME/ros2_livox_ws"
INSTALL_DIR="/opt/ros/rolling"

echo "=== ROS 2 Livox Workspace Setup ==="

# Check if ROS 2 is installed
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ ROS 2 not found at $INSTALL_DIR"
    echo "Install ROS 2 first: sudo apt install ros-rolling-desktop"
    exit 1
fi

# Source ROS 2
source "$INSTALL_DIR/setup.bash"

# Create workspace
mkdir -p "$ROS2_WS/src"
cd "$ROS2_WS"

echo "✓ Workspace created at $ROS2_WS"

# Clone Livox ROS 2 driver
cd "$ROS2_WS/src"
if [ ! -d "livox_ros_driver2" ]; then
    echo "Cloning Livox ROS 2 driver..."
    git clone https://github.com/Livox-SDK/livox_ros_driver2.git
else
    echo "✓ Livox driver already exists"
fi

# Build workspace
cd "$ROS2_WS"
echo "Building workspace... (this may take a few minutes)"
colcon build --symlink-install

echo ""
echo "✓ Setup complete!"
echo ""
echo "To use this workspace, run:"
echo "  source $ROS2_WS/install/setup.bash"
echo ""
echo "Then launch Livox:"
echo "  ros2 launch livox_ros_driver2 rviz_launch.py"
