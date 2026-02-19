#!/bin/bash
# Livox Mid 360 - Universal Launcher
# Choose between Open3D and RViz visualization

cd "$(dirname "$0")"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         Livox Mid 360 - Choose Visualization Mode            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "  1) RViz (Professional visualization) - RECOMMENDED"
echo "  2) Open3D (Simple 3D mapper)"
echo "  3) Python Packet Sniffer (Debug mode)"
echo ""
echo -n "Select option (1-3): "
read -r choice

case $choice in
    1)
        echo ""
        echo "Starting ROS 2 + RViz..."
        echo ""
        exec ./livox_rviz_launcher.sh
        ;;
    2)
        echo ""
        echo "Starting Livox with Open3D..."
        echo ""
        exec ./livox_launcher.sh
        ;;
    3)
        echo ""
        echo "Starting Livox SDK and Packet Sniffer..."
        echo ""
        ./Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start \
            ./Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json &
        SDK_PID=$!
        sleep 2
        source venv/bin/activate
        python3 livox_packet_sniffer.py
        kill $SDK_PID 2>/dev/null
        ;;
    *)
        echo "Invalid option. Exiting."
        exit 1
        ;;
esac
