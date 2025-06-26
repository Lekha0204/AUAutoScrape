#!/usr/bin/env python3
"""
Local development server for Student Result Analysis System
Run this file to start the application locally
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables for local development
os.environ.setdefault('SESSION_SECRET', 'your-development-secret-key-change-in-production')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('FLASK_DEBUG', '1')

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("Starting Student Result Analysis System...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )