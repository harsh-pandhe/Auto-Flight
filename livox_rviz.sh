#!/bin/bash
# Livox Mid 360 + RViz Visualization
# One-command RViz setup with Livox point cloud

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 + RViz                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check ROS 2
if [ ! -f /opt/ros/rolling/setup.bash ]; then
    echo "❌ ROS 2 rolling not found!"
    exit 1
fi

# Setup ROS 2
unset ROS_DISTRO COLCON_PREFIX_PATH
if [ -n "${ZSH_VERSION:-}" ] && [ -f /opt/ros/rolling/setup.zsh ]; then
    source /opt/ros/rolling/setup.zsh > /dev/null 2>&1
else
    source /opt/ros/rolling/setup.bash > /dev/null 2>&1
fi

if [ -f ~/ros2_livox_ws/install/setup.zsh ]; then
    source ~/ros2_livox_ws/install/setup.zsh > /dev/null 2>&1
else
    source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
fi

# Filter out humble paths
export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')

echo "Starting Livox driver..."
# Start driver in background
(
    unset ROS_DISTRO COLCON_PREFIX_PATH
    if [ -n "${ZSH_VERSION:-}" ] && [ -f /opt/ros/rolling/setup.zsh ]; then
        source /opt/ros/rolling/setup.zsh > /dev/null 2>&1
    else
        source /opt/ros/rolling/setup.bash > /dev/null 2>&1
    fi
    if [ -f ~/ros2_livox_ws/install/setup.zsh ]; then
        source ~/ros2_livox_ws/install/setup.zsh > /dev/null 2>&1
    else
        source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
    fi
    export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    
    ~/ros2_livox_ws/install/livox_ros2_python_driver/bin/livox_driver_node
) >/dev/null 2>&1 &

DRIVER_PID=$!
sleep 3

# Verify driver is running
if ! kill -0 $DRIVER_PID 2>/dev/null; then
    echo "❌ Driver failed to start!"
    exit 1
fi

echo "✓ Driver running (PID: $DRIVER_PID)"
echo ""
echo "Launching RViz..."
echo ""

# Check if RViz config exists
if [ ! -f "$SCRIPT_DIR/livox_rviz_config.rviz" ]; then
    echo "⚠️  Warning: livox_rviz_config.rviz not found"
    echo "Launching RViz without saved config..."
    rviz2
else
    echo "Using config: $SCRIPT_DIR/livox_rviz_config.rviz"
    rviz2 -d "$SCRIPT_DIR/livox_rviz_config.rviz"
fi

# Cleanup on exit
trap "kill $DRIVER_PID 2>/dev/null; exit" INT TERM EXIT
echo ""
echo "Shutting down..."
