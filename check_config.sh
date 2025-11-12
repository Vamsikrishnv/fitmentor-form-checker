#!/bin/bash
echo "==================================================================="
echo "   FitMentor Video Processing - Configuration Check"
echo "==================================================================="
echo ""

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded .env file"
else
    echo "❌ No .env file found!"
    echo "   Run: cp .env.example .env"
    exit 1
fi

echo ""
echo "Current Performance Settings:"
echo "----------------------------"
echo "FRAME_SKIP_RATE = ${FRAME_SKIP_RATE:-6}"
echo "MAX_FRAMES_TO_ANALYZE = ${MAX_FRAMES_TO_ANALYZE:-300}"  
echo "VIDEO_RESIZE_WIDTH = ${VIDEO_RESIZE_WIDTH:-640}"
echo "MIN_FRAMES_FOR_ANALYSIS = ${MIN_FRAMES_FOR_ANALYSIS:-30}"

echo ""
echo "Performance Analysis:"
echo "----------------------------"

SKIP=${FRAME_SKIP_RATE:-6}
MAX_FRAMES=${MAX_FRAMES_TO_ANALYZE:-300}
WIDTH=${VIDEO_RESIZE_WIDTH:-640}

# Calculate metrics
FRAMES_PER_SEC=$(echo "scale=1; 30 / $SKIP" | bc)
VIDEO_COVERAGE=$(echo "scale=0; $MAX_FRAMES / $FRAMES_PER_SEC" | bc)

echo "At 30 FPS video:"
echo "  • Analyzing $FRAMES_PER_SEC frames per second"
echo "  • Max coverage: ${VIDEO_COVERAGE}s of video"
echo "  • Resolution: ${WIDTH}px width"

echo ""
echo "Expected Processing Times:"
echo "----------------------------"
if [ "$SKIP" -ge 10 ]; then
    echo "  10s video: 1.5-2.5 seconds ⚡ ULTRA FAST"
    echo "  30s video: 2-3 seconds"
    echo "  60s video: 2.5-4 seconds"
elif [ "$SKIP" -ge 8 ]; then
    echo "  10s video: 2-3 seconds ⚡ VERY FAST"
    echo "  30s video: 2.5-4 seconds"
    echo "  60s video: 3-5 seconds"
elif [ "$SKIP" -ge 6 ]; then
    echo "  10s video: 2-3 seconds ⚡ FAST (recommended)"
    echo "  30s video: 3-5 seconds"
    echo "  60s video: 4-6 seconds"
else
    echo "  10s video: 3-5 seconds ⚙️  BALANCED"
    echo "  30s video: 5-8 seconds"
    echo "  60s video: 6-10 seconds"
fi

echo ""
echo "==================================================================="
echo "   Performance Presets"
echo "==================================================================="
echo ""
echo "To switch to ULTRA FAST mode (1.5-3s):"
echo "  cp .env.ultrafast .env"
echo "  Then restart your server"
echo ""
echo "Or manually edit .env with these values:"
echo "----------------------------"
echo "FRAME_SKIP_RATE=10"
echo "MAX_FRAMES_TO_ANALYZE=150"
echo "VIDEO_RESIZE_WIDTH=480"
echo "MIN_FRAMES_FOR_ANALYSIS=15"
echo ""
