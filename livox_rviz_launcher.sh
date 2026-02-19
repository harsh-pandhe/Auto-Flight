#!/bin/bash
# Livox + ROS 2 + RViz Launcher
# Streams Livox data to ROS 2 and visualizes in RViz

set -e
cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + ROS 2 + RViz                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Try both Humble and Rolling ROS 2 installations
if [ -f /opt/ros/humble/setup.bash ]; then
    ROS_DISTRO="humble"
    ROS_SETUP="/opt/ros/humble/setup.bash"
elif [ -f /opt/ros/rolling/setup.bash ]; then
    ROS_DISTRO="rolling"
    ROS_SETUP="/opt/ros/rolling/setup.bash"
else
    echo "❌ ROS 2 not found at /opt/ros/"
    echo "   Install ROS 2 first: https://docs.ros.org/en/humble/Installation.html"
    exit 1
fi

echo "Using ROS 2 $ROS_DISTRO"
echo ""

# Source ROS 2 environment
source "$ROS_SETUP"

# Start SDK in background
echo "Starting Livox SDK..."
./Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start \
    ./Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json &
SDK_PID=$!
echo "✓ SDK started (PID: $SDK_PID)"
sleep 2

# Start ROS 2 driver
echo "Starting ROS 2 Livox driver..."
source ~/ros2_livox_ws/install/setup.bash
ros2 run livox_ros2_python_driver livox_driver_node &
DRIVER_PID=$!
echo "✓ Driver started (PID: $DRIVER_PID)"
sleep 2

# Start RViz with Livox configuration
echo "Starting RViz..."
if [ -f ./livox_rviz_config.rviz ]; then
    rviz2 -d ./livox_rviz_config.rviz &
else
    rviz2 &
fi
RVIZ_PID=$!
echo "✓ RViz started (PID: $RVIZ_PID)"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  All systems active:                                       ║"
echo "║  • Livox SDK (PID $SDK_PID)                       ║"
echo "║  • ROS 2 Driver (PID $DRIVER_PID)                   ║"
echo "║  • RViz (PID $RVIZ_PID)                           ║"
echo "║                                                            ║"
echo "║  In RViz:                                                  ║"
echo "║  1. Add PointCloud2 display                               ║"
echo "║  2. Set Topic to: /livox/lidar                            ║"
echo "║  3. Set Fixed Frame to: livox_frame                       ║"
echo "║                                                            ║"
echo "║  Press Ctrl+C to stop all services                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Keep script alive and handle cleanup
trap "echo 'Shutting down...'; kill $SDK_PID $DRIVER_PID $RVIZ_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
