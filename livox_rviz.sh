#!/bin/bash
# Livox Mid 360 - Visualization
# Uses Open3D (Terminal GUI) or RViz (if available)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Livox Mid 360 - Visualization                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Check what's available
if command -v rviz2 >/dev/null 2>&1; then
    echo "✓ RViz found - using RViz visualization"
    USE_RVIZ=1
else
    echo "ℹ RViz not installed - using Open3D visualization instead"
    USE_RVIZ=0
fi
echo ""

if [ $USE_RVIZ -eq 1 ]; then
    # ============ RViz Path ============
    
    # Check ROS 2
    if [ ! -f /opt/ros/rolling/setup.bash ]; then
        echo "❌ ROS 2 rolling not found"
        exit 1
    fi
    
    echo "Setting up ROS 2 environment..."
    unset ROS_DISTRO COLCON_PREFIX_PATH
    source /opt/ros/rolling/setup.bash
    
    if [ -f ~/ros2_livox_ws/install/setup.bash ]; then
        source ~/ros2_livox_ws/install/setup.bash
    fi
    
    export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
    
    echo "Starting Livox ROS 2 driver..."
    (
        unset ROS_DISTRO COLCON_PREFIX_PATH
        source /opt/ros/rolling/setup.bash > /dev/null 2>&1
        source ~/ros2_livox_ws/install/setup.bash > /dev/null 2>&1
        export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
        export PYTHONPATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v "/opt/ros/humble" | tr '\n' ':' | sed 's/:$//')
        ~/ros2_livox_ws/install/livox_ros2_python_driver/bin/livox_driver_node
    ) >/tmp/livox_driver_rviz.log 2>&1 &
    
    DRIVER_PID=$!
    sleep 3
    
    if ! kill -0 $DRIVER_PID 2>/dev/null; then
        echo "❌ Driver failed"
        tail -20 /tmp/livox_driver_rviz.log
        exit 1
    fi
    
    echo "✓ Driver running"
    echo "Launching RViz with Livox config..."
    
    if [ -f "$SCRIPT_DIR/livox_rviz_config.rviz" ]; then
        rviz2 -d "$SCRIPT_DIR/livox_rviz_config.rviz"
    else
        rviz2
    fi
    
    trap "kill $DRIVER_PID 2>/dev/null" EXIT
    
else
    # ============ Open3D Path (Fallback) ============
    echo "Starting Livox with Open3D visualization..."
    echo "Controls: Left=Rotate, Right=Pan, Scroll=Zoom, Q=Quit"
    echo ""
    
    source venv/bin/activate 2>/dev/null || echo "Warning: venv not activated"
    
    # Start SDK in background
    ./Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start \
        ./Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json >/dev/null 2>&1 &
    
    SDK_PID=$!
    sleep 2
    
    # Start visualization
    python3 livox_3d_mapper.py
    
    # Cleanup
    kill $SDK_PID 2>/dev/null
    echo "Done"
fi
