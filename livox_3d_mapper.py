#!/usr/bin/env python3
"""
Livox Mid 360 3D Mapping Script
Connects to Livox Mid 360 via Ethernet and creates a real-time 3D point cloud map.
"""

import socket
import struct
import numpy as np
import threading
import time
from collections import deque
import open3d as o3d

# Livox Mid 360 default settings
LIVOX_IP = "192.168.1.199"  # Livox IP from arp-scan
LIVOX_PORT = 56301  # Mid-360 point cloud port from SDK config
BUFFER_SIZE = 65536

class LivoxMid360:
    def __init__(self, ip=LIVOX_IP, port=LIVOX_PORT, max_points=100000):
        self.ip = ip
        self.port = port
        self.socket = None
        self.running = False
        self.points = deque(maxlen=max_points)
        self.lock = threading.Lock()
        self.connected = False
        self.packet_count = 0
        self.last_packet_time = 0.0
        
    def connect(self):
        """Connect to Livox Mid 360"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.settimeout(2.0)
            # Bind to receive UDP packets from the sensor
            self.socket.bind(("0.0.0.0", self.port))
            print(f"Attempting to connect to Livox at {self.ip}:{self.port}")
            # Send a simple handshake
            self.socket.sendto(b'\x00', (self.ip, self.port))
            self.connected = True
            print("✓ Connected to Livox Mid 360")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            print(f"  Check if Livox is at {self.ip} and accessible via Ethernet")
            return False
    
    def parse_point_cloud(self, data):
        """Parse Livox point cloud data packet"""
        points = []
        try:
            # Livox SDK2 ethernet packet header
            header_fmt = "<B H H H H B B B 12s I 8s"
            header_size = struct.calcsize(header_fmt)
            if len(data) < header_size:
                return points

            (
                version,
                length,
                time_interval,
                dot_num,
                udp_cnt,
                frame_cnt,
                data_type,
                time_type,
                _rsvd,
                _crc32,
                _timestamp,
            ) = struct.unpack_from(header_fmt, data, 0)

            offset = header_size
            if data_type == 0x01:  # Cartesian high: int32 mm
                point_fmt = "<iiiBB"
                point_size = struct.calcsize(point_fmt)
                for _ in range(dot_num):
                    if offset + point_size > len(data):
                        break
                    x, y, z, _reflectivity, _tag = struct.unpack_from(point_fmt, data, offset)
                    points.append([x / 1000.0, y / 1000.0, z / 1000.0])
                    offset += point_size
            elif data_type == 0x02:  # Cartesian low: int16 cm
                point_fmt = "<hhhBB"
                point_size = struct.calcsize(point_fmt)
                for _ in range(dot_num):
                    if offset + point_size > len(data):
                        break
                    x, y, z, _reflectivity, _tag = struct.unpack_from(point_fmt, data, offset)
                    points.append([x / 100.0, y / 100.0, z / 100.0])
                    offset += point_size
            else:
                return points
            
            return points
        except Exception as e:
            print(f"Parse error: {e}")
            return points
    
    def receive_data(self):
        """Receive point cloud data in background thread"""
        print("Starting data reception...")
        while self.running and self.connected:
            try:
                data, addr = self.socket.recvfrom(BUFFER_SIZE)
                self.packet_count += 1
                self.last_packet_time = time.time()
                points = self.parse_point_cloud(data)
                
                with self.lock:
                    for point in points:
                        self.points.append(point)
                
                if points:
                    print(f"Received {len(points)} points, total: {len(self.points)}")
                elif self.packet_count % 50 == 0:
                    print(f"Packets received: {self.packet_count}, last size: {len(data)} bytes")
                    
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Reception error: {e}")
                break
        
        print("Data reception stopped")
    
    def start(self):
        """Start receiving data"""
        if not self.connected:
            if not self.connect():
                return False
        
        self.running = True
        thread = threading.Thread(target=self.receive_data, daemon=True)
        thread.start()
        return True
    
    def stop(self):
        """Stop receiving data"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("Livox connection closed")
    
    def get_points(self):
        """Get current point cloud as numpy array"""
        with self.lock:
            if len(self.points) > 0:
                return np.array(list(self.points))
            return np.array([])


class PointCloudVisualizer:
    def __init__(self, livox):
        self.livox = livox
        self.vis = o3d.visualization.Visualizer()
        self.pcd = o3d.geometry.PointCloud()
        self.first_update = True
        
    def setup_visualizer(self):
        """Initialize Open3D visualizer"""
        try:
            self.vis.create_window(window_name="Livox Mid 360 3D Map", width=1280, height=960)
            self.vis.get_render_option().point_size = 2.0
            self.vis.get_render_option().background_color = np.array([0, 0, 0])
            
            # Add coordinate frame
            mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
                size=0.5, origin=[0, 0, 0])
            self.vis.add_geometry(mesh_frame)
            
            return True
        except Exception as e:
            print(f"Visualizer setup error: {e}")
            return False
    
    def update_visualization(self):
        """Update point cloud visualization"""
        points = self.livox.get_points()

        if len(points) > 0:
            # Create point cloud object
            self.pcd.points = o3d.utility.Vector3dVector(points)

            # Color points based on height (z) for better visualization
            colors = np.zeros((len(points), 3))
            z_values = points[:, 2]
            z_min, z_max = z_values.min(), z_values.max()

            if z_max > z_min:
                # Normalize z between 0 and 1 for coloring
                z_normalized = (z_values - z_min) / (z_max - z_min)
                colors[:, 0] = z_normalized  # Red based on height
                colors[:, 1] = 1 - z_normalized  # Inverse green

            self.pcd.colors = o3d.utility.Vector3dVector(colors)

            if self.first_update:
                self.vis.add_geometry(self.pcd)
                self.first_update = False
            else:
                self.vis.update_geometry(self.pcd)

        # Always poll events so the window stays responsive
        if not self.vis.poll_events():
            return False
        self.vis.update_renderer()

        return True
    
    def run(self):
        """Run visualization loop"""
        if not self.setup_visualizer():
            return
        
        print("Visualization started. Press Ctrl+C or close window to exit.")
        print("Controls:")
        print("  Mouse left: Rotate")
        print("  Mouse right: Pan")
        print("  Scroll: Zoom")
        
        try:
            while self.livox.running:
                if not self.update_visualization():
                    break
                time.sleep(0.05)  # ~20 FPS update rate
        except KeyboardInterrupt:
            print("\nVisualization stopped by user")
        finally:
            self.vis.destroy_window()


def main():
    """Main function"""
    print("=" * 60)
    print("Livox Mid 360 3D Mapper")
    print("=" * 60)
    
    # Create Livox connection
    livox = LivoxMid360(ip=LIVOX_IP, port=LIVOX_PORT)
    
    # Start data reception
    if not livox.start():
        print("Failed to start Livox connection")
        return
    
    # Give it a moment to start receiving data
    time.sleep(1)
    
    # Start visualization
    visualizer = PointCloudVisualizer(livox)
    
    try:
        visualizer.run()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        livox.stop()
        print("Goodbye!")


if __name__ == "__main__":
    main()
