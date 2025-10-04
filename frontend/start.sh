#!/bin/bash

# Embiggen Your Eyes - Quick Start Script
# NASA Space Apps Challenge 2025

echo "=================================="
echo "Embiggen Your Eyes - Frontend"
echo "NASA Space Apps Challenge 2025"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "index.html" ]; then
    echo "Error: index.html not found. Please run this script from the frontend directory."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0
    else
        return 1
    fi
}

PORT=8000

# Check if port is already in use
if check_port $PORT; then
    echo "⚠️  Port $PORT is already in use."
    echo "Please stop the other server or choose a different port."
    exit 1
fi

echo "Starting development server on port $PORT..."
echo ""

# Try Python 3 first
if command -v python3 &> /dev/null; then
    echo "Using Python 3 HTTP server..."
    echo ""
    echo "🚀 Server starting at: http://localhost:$PORT"
    echo "📍 Press Ctrl+C to stop the server"
    echo ""
    python3 -m http.server $PORT
# Try Python 2
elif command -v python &> /dev/null; then
    echo "Using Python 2 HTTP server..."
    echo ""
    echo "🚀 Server starting at: http://localhost:$PORT"
    echo "📍 Press Ctrl+C to stop the server"
    echo ""
    python -m SimpleHTTPServer $PORT
# Try PHP
elif command -v php &> /dev/null; then
    echo "Using PHP built-in server..."
    echo ""
    echo "🚀 Server starting at: http://localhost:$PORT"
    echo "📍 Press Ctrl+C to stop the server"
    echo ""
    php -S localhost:$PORT
# Try Node.js
elif command -v node &> /dev/null; then
    echo "Using Node.js http-server..."
    echo "Installing http-server (if not already installed)..."
    npx http-server -p $PORT
else
    echo "❌ Error: No suitable HTTP server found."
    echo ""
    echo "Please install one of the following:"
    echo "  - Python 3: https://www.python.org/downloads/"
    echo "  - Node.js: https://nodejs.org/"
    echo "  - PHP: https://www.php.net/downloads"
    exit 1
fi

