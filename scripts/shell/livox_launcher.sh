#!/bin/bash
# Livox Mid 360 Complete Launcher
# Starts SDK and 3D mapper in background

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "╔════════════════════════════════════════╗"
echo "║  Livox Mid 360 - Complete Launcher    ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Start SDK in background
echo "Starting Livox SDK..."
"$REPO_ROOT/Livox-SDK2/build/samples/livox_lidar_quick_start/livox_lidar_quick_start" \
    "$REPO_ROOT/Livox-SDK2/samples/livox_lidar_quick_start/mid360_config.json" &
SDK_PID=$!
echo "✓ SDK started (PID: $SDK_PID)"
echo ""

# Wait for SDK to initialize
sleep 2

# Start mapper in background
echo "Starting 3D Mapper..."
source "$REPO_ROOT/venv/bin/activate"
python3 "$REPO_ROOT/scripts/python/livox_3d_mapper.py" &
MAPPER_PID=$!
echo "✓ Mapper started (PID: $MAPPER_PID)"
echo ""

echo "╔════════════════════════════════════════╗"
echo "║  System Active                         ║"
echo "╠════════════════════════════════════════╣"
echo "║ SDK:   PID $SDK_PID                 ║"
echo "║ Mapper: PID $MAPPER_PID             ║"
echo "║                                        ║"
echo "║ Open3D window is streaming 3D data    ║"
echo "║ Press Ctrl+C to stop all services    ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Keep script alive and handle cleanup
trap "kill $SDK_PID $MAPPER_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
