import pandas as pd

def plot_vibration_throttle(csv_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Define the required columns
    vibration_column = 'Vib_Z'
    throttle_column = 'Thr_PWM'
    
    # Check if the required columns exist in the DataFrame
    if not all(col in df.columns for col in [vibration_column, throttle_column]):
        raise ValueError(f'Missing cols: {required_columns}')
    
    # Plot the data
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 6))
    plt.plot(df[throttle_column], df[vibration_column], label='Vib_Z vs Thr_PWM')
    plt.xlabel('Thr_PWM')
    plt.ylabel('Vib_Z')
    plt.title('Z-axis Vibration vs Motor Throttle/PWM')
    plt.legend()
    plt.grid(True)
    
    # Save the plot to a file
    plt.savefig('/workspace/scripts/vibe_throttle_plot.png')
    print("Plot saved as /workspace/scripts/vibe_throttle_plot.png")

def main():
    csv_file = '/workspace/data/telemetry/telemetry_20260313_184416.csv'
    plot_vibration_throttle(csv_file)

if __name__ == '__main__':
    main()
