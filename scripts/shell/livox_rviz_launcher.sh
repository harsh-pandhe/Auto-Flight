#!/bin/bash
# Livox + ROS 2 + RViz Launcher (Fixed Environment)
# Clean ROS 2 setup to avoid venv interference

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)" || exit 1
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)" || exit 1
cd "$REPO_ROOT" || exit 1

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 + RViz                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Find ROS 2 installation
ROS_SETUP=""
if [ -f /opt/ros/rolling/setup.bash ]; then
    ROS_SETUP="/opt/ros/rolling/setup.bash"
    ROS_DISTRO="rolling"
elif [ -f /opt/ros/humble/setup.bash ]; then
    ROS_SETUP="/opt/ros/humble/setup.bash"
    ROS_DISTRO="humble"
else
    echo "❌ ROS 2 not found! Tried /opt/ros/{rolling,humble}"
    exit 1
fi

echo "Using ROS 2 $ROS_DISTRO"
echo ""

# Start Livox SDK (doesn't need ROS 2)
echo "Starting Livox SDK..."
"$REPO_ROOT/Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start" \
    "$REPO_ROOT/Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json" > /tmp/livox_sdk.log 2>&1 &
SDK_PID=$!
echo "✓ SDK started (PID: $SDK_PID)"
sleep 3

# Start ROS 2 driver and RViz in clean ROS 2 environment
echo "Starting ROS 2 driver and RViz..."
exec bash << ROSSHELL
source "$ROS_SETUP"
source "\$HOME/ros2_livox_ws/install/setup.bash"

echo "✓ ROS 2 environment sourced"

# Start driver
echo "Starting Livox ROS 2 driver..."
ros2 run livox_ros2_python_driver livox_driver_node > /tmp/livox_driver.log 2>&1 &
DRIVER_PID=\$!
echo "✓ Driver started (PID: \$DRIVER_PID)"
sleep 2

# Start RViz
echo "Starting RViz..."
if [ -f "$REPO_ROOT/config/livox_rviz_config.rviz" ]; then
    rviz2 -d "$REPO_ROOT/config/livox_rviz_config.rviz"
else
    rviz2
fi

# Cleanup
kill $SDK_PID \$DRIVER_PID 2>/dev/null
ROSSHELL
