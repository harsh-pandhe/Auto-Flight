# ROS 2 Livox Mid-360 Setup

Once ROS 2 is installed, run the workspace setup script:

```bash
chmod +x ros2_ws_setup.sh
./ros2_ws_setup.sh
```

This will:
1. Create a ROS 2 workspace
2. Clone the official Livox ROS 2 driver
3. Build it with colcon
4. Set up RViz visualization

## Quick Start

```bash
# Source ROS 2
source /opt/ros/rolling/setup.bash

# Source workspace
source ~/ros2_livox_ws/install/setup.bash

# Launch Livox driver with RViz
ros2 launch livox_ros_driver2 rviz_launch.py

# In another terminal, view sensor topics
ros2 topic list
ros2 topic echo /livox/lidar
```

## Hardware Setup

The Livox Mid 360 should be on `192.168.1.199` (from earlier network discovery).

In RViz:
- Set Fixed Frame: `livox_frame`
- Add PointCloud2 display: `/livox/lidar`
- Color by Intensity or Height

## Next Steps

- **SLAM**: Use LIO-SAM or FAST-LIO2 for 3D mapping
- **RVIZ2**: Add custom plugins for advanced visualization
- **Python ROS2 Node**: Create custom processing nodes

