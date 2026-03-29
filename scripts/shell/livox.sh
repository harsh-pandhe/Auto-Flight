#!/bin/bash
# Livox Mid 360 - Universal Launcher
# Choose between multiple visualization modes

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         Livox Mid 360 - Choose Visualization Mode            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "  1) Open3D 3D Mapper (RECOMMENDED - most reliable)"
echo "  2) ROS 2 Driver (Data streaming, may require RViz setup)"
echo "  3) Python Packet Sniffer (Debug UDP packets)"
echo ""
echo -n "Select option (1-3): "
read -r choice

case $choice in
    1)
        echo ""
        echo "Starting Livox with Open3D real-time 3D visualization..."
        echo ""
        exec "$REPO_ROOT/scripts/shell/livox_launcher.sh"
        ;;
    2)
        echo ""
        echo "Starting ROS 2 Livox driver..."
        echo ""
        # Source the setup script and start interactive shell with ROS 2 environment
        exec bash -c "source '$REPO_ROOT/scripts/shell/livox_ros2.sh'; exec bash"
        ;;
    3)
        echo ""
        echo "Starting Livox SDK and Packet Sniffer..."
        echo ""
        "$REPO_ROOT/Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start" \
            "$REPO_ROOT/Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json" &
        SDK_PID=$!
        sleep 2
        source "$REPO_ROOT/venv/bin/activate"
        python3 "$REPO_ROOT/scripts/python/livox_packet_sniffer.py"
        kill $SDK_PID 2>/dev/null
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac
