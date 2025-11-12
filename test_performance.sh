#!/bin/bash
# Quick test script to verify performance optimizations

echo "=== FitMentor Video Processing Performance Test ==="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "✅ .env file exists"
fi

echo ""
echo "Current performance settings:"
echo "----------------------------"
source .env 2>/dev/null || true

echo "FRAME_SKIP_RATE: ${FRAME_SKIP_RATE:-6 (default)}"
echo "MAX_FRAMES_TO_ANALYZE: ${MAX_FRAMES_TO_ANALYZE:-300 (default)}"
echo "VIDEO_RESIZE_WIDTH: ${VIDEO_RESIZE_WIDTH:-640 (default)}"
echo "MIN_FRAMES_FOR_ANALYSIS: ${MIN_FRAMES_FOR_ANALYSIS:-30 (default)}"

echo ""
echo "Expected performance:"
echo "  - 10s video: 2-3 seconds"
echo "  - 30s video: 3-5 seconds"
echo "  - 60s video: 4-6 seconds"

echo ""
echo "If still slow, try ULTRA FAST mode:"
echo "-----------------------------------"
echo "Add to your .env file:"
echo "FRAME_SKIP_RATE=8"
echo "MAX_FRAMES_TO_ANALYZE=200"
echo "VIDEO_RESIZE_WIDTH=480"
echo "MIN_FRAMES_FOR_ANALYSIS=20"

echo ""
echo "To test the API:"
echo "uvicorn backend.main:app --reload"
