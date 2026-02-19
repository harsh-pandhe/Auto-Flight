#!/usr/bin/env python3
"""Record /livox/lidar PointCloud2 data to CSV.

Usage (after sourcing ROS 2 env):
  python3 livox_csv_recorder.py --output flight_data.csv --max-frames 300
"""

import argparse
import csv
import sys
from typing import Optional

import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record /livox/lidar to CSV")
    parser.add_argument(
        "--output",
        default="livox_points.csv",
        help="Output CSV path (default: livox_points.csv)",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=0,
        help="Stop after N frames (0 = unlimited)",
    )
    return parser.parse_args()


class LivoxCsvRecorder:
    def __init__(self, output_path: str, max_frames: int) -> None:
        self.output_path = output_path
        self.max_frames = max_frames
        self.frame_count = 0
        self.point_count = 0
        self.csv_file = open(self.output_path, "w", newline="")
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(["stamp", "frame_id", "x", "y", "z", "intensity"])

        self.node = rclpy.create_node("livox_csv_recorder")
        self.sub = self.node.create_subscription(
            PointCloud2,
            "/livox/lidar",
            self.on_pointcloud,
            qos_profile_sensor_data,
        )

    def close(self) -> None:
        self.csv_file.close()
        self.node.destroy_node()

    def on_pointcloud(self, msg: PointCloud2) -> None:
        self.frame_count += 1
        stamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        frame_id = msg.header.frame_id

        for x, y, z, intensity in point_cloud2.read_points(
            msg,
            field_names=("x", "y", "z", "intensity"),
            skip_nans=True,
        ):
            self.writer.writerow([stamp, frame_id, x, y, z, intensity])
            self.point_count += 1

        self.csv_file.flush()

        if self.max_frames and self.frame_count >= self.max_frames:
            raise SystemExit


def main() -> int:
    args = parse_args()
    rclpy.init()
    recorder: Optional[LivoxCsvRecorder] = None

    try:
        recorder = LivoxCsvRecorder(args.output, args.max_frames)
        rclpy.spin(recorder.node)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        if recorder:
            recorder.close()
        rclpy.shutdown()

    return 0


if __name__ == "__main__":
    sys.exit(main())
