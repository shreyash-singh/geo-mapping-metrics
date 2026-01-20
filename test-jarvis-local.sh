#!/bin/bash
# Test Jarvis locally before deploying

echo "🧪 Testing Jarvis locally..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed. Installing dependencies..."
    pip3 install -r requirements.txt
fi

# Start the server
echo "🚀 Starting Jarvis on http://localhost:5001"
echo "Press Ctrl+C to stop"
echo ""
python3 jarvis_app.py
