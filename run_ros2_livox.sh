#!/bin/bash
# ROS 2 Livox Driver Launcher
# Note: Requires full ROS 2 installation with rclpy support
# For now, use ./livox_launcher.sh instead for 3D mapping

echo "Note: ROS 2 driver requires rclpy which is not in Humble system Python"
echo ""
echo "For 3D mapping, use instead:"
echo "  ./livox_launcher.sh"
echo ""
echo "Or run manually:"
echo "  1. ./Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start ./Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json"
echo "  2. source venv/bin/activate && python3 livox_3d_mapper.py"
