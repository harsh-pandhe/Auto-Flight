#!/bin/bash
echo "🚀 ISRO AI Swarm Initializing..."

while true; do
    echo "----------------------------------------"
    echo "🧠 Waking up @ROS-Engineer..."
    
    # We are spoon-feeding it the exact task and forbidding any other tools.
    ollama launch claude --model qwen3-coder -- \
    "You are the @ROS-Engineer for the ISRO ASCEND 2026 project. 
    Your ONLY task is to write a Python script using OpenCV to detect the color RED (for ISRO Task 3). 
    The script should use the webcam, define the HSV bounds for red, draw a bounding box around the detected object, and print 'ISRO TARGET ACQUIRED' to the terminal.
    
    DO NOT read any files. DO NOT output conversational text. DO NOT ask for permission.
    Immediately use your 'write_file' tool to save this code as 'isro_red_detector.py' in the current directory. Once the file is saved, exit."

    echo "💤 Swarm is resting for 60 seconds before next cycle..."
    sleep 60
done