import pandas as pd
import matplotlib.pyplot as plt

# Load your Stage 1 Flight Data
CSV_FILE = "stage1_telemetry_log.csv"
try:
    df = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    print(f"Could not find {CSV_FILE}. Make sure you are in the right folder!")
    exit()

# Start the Plotting Window
fig = plt.figure(figsize=(12, 6))
fig.canvas.manager.set_window_title('Project ASCEND - Flight Telemetry')

# --- PLOT 1: The 3D SLAM Map Path ---
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot(df['LiDAR_X'], df['LiDAR_Y'], df['LiDAR_Z'], label='FAST-LIO Path', color='cyan', linewidth=2)
ax1.scatter(df['LiDAR_X'].iloc[0], df['LiDAR_Y'].iloc[0], df['LiDAR_Z'].iloc[0], color='green', s=100, label='Start')
ax1.scatter(df['LiDAR_X'].iloc[-1], df['LiDAR_Y'].iloc[-1], df['LiDAR_Z'].iloc[-1], color='red', s=100, label='End')

# Set background to dark mode for the 3D plot
ax1.set_facecolor('#1e1e1e')
ax1.xaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
ax1.yaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
ax1.zaxis.set_pane_color((0.1, 0.1, 0.1, 1.0))
ax1.tick_params(colors='white')

ax1.set_xlabel('X (meters)', color='white')
ax1.set_ylabel('Y (meters)', color='white')
ax1.set_zlabel('Altitude (meters)', color='white')
ax1.set_title('Drone 3D Trajectory', color='white', pad=20)
ax1.legend(facecolor='#1e1e1e', labelcolor='white')

# --- PLOT 2: Altitude vs Flow Quality ---
# Normalize time to start at 0 seconds
time_seconds = df['Timestamp'] - df['Timestamp'].iloc[0]

ax2 = fig.add_subplot(222)
ax2.plot(time_seconds, df['LiDAR_Z'], color='#00ff00', linewidth=2)
ax2.set_facecolor('#1e1e1e')
ax2.tick_params(colors='white')
ax2.set_title('FAST-LIO Altitude (Z)', color='white')
ax2.set_ylabel('Meters', color='white')
ax2.grid(color='#333333')

ax3 = fig.add_subplot(224)
ax3.plot(time_seconds, df['Flow_Qual'], color='#ff9900', linewidth=2)
ax3.set_facecolor('#1e1e1e')
ax3.tick_params(colors='white')
ax3.set_title('Optical Flow Sensor Quality', color='white')
ax3.set_ylabel('Signal Strength (0-255)', color='white')
ax3.set_xlabel('Flight Time (Seconds)', color='white')
ax3.grid(color='#333333')

# Set main window background
fig.patch.set_facecolor('#121212')
plt.tight_layout()
plt.show()