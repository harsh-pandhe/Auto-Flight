import pandas as pd
import matplotlib.pyplot as plt

# 1. Load your flight log
df = pd.read_csv('ascend_flight_log.csv')

# 2. Integrate Velocities to get local (X, Y) coordinates
df['dt'] = df['timestamp'].diff().fillna(0)
df['x_pos'] = (df['vx'] * df['dt']).cumsum()
df['y_pos'] = (df['vy'] * df['dt']).cumsum()

# 3. Setup 3D Plot
fig = plt.figure(figsize=(12, 9))
ax = fig.add_subplot(111, projection='3d') # Use add_subplot

# Plot the 3D trajectory
ax.plot(df['x_pos'], df['y_pos'], df['alt'], label='Drone Path', color='blue', linewidth=2)

# Scatter points for better depth perception
ax.scatter(df['x_pos'], df['y_pos'], df['alt'], c=df['alt'], cmap='viridis', s=10)

# Mark Start and End points
ax.scatter(df['x_pos'].iloc[0], df['y_pos'].iloc[0], df['alt'].iloc[0], color='green', s=150, label='Start (Home)')
ax.scatter(df['x_pos'].iloc[-1], df['y_pos'].iloc[-1], df['alt'].iloc[-1], color='red', s=150, label='End')

ax.set_xlabel('X Position (m)')
ax.set_ylabel('Y Position (m)')
ax.set_zlabel('Altitude (m)')
ax.set_title('Project ASCEND: 3D Flight Validation')
ax.legend()

plt.show()  