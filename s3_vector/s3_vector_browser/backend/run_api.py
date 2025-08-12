#!/usr/bin/env python3
"""
Simple launcher for the FastAPI backend server
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the FastAPI server"""
    current_dir = Path(__file__).parent
    
    print("Starting S3 Vector Browser API Server...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    print("-" * 50)
    
    try:
        # Run the API server
        subprocess.run([
            sys.executable, 
            str(current_dir / "api_server.py"),
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\nShutting down API server...")
    except subprocess.CalledProcessError as e:
        print(f"Error running API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()