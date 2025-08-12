#!/usr/bin/env python3
"""
Simple HTTP server for S3 Vector Browser JavaScript Frontend
"""

import http.server
import socketserver
import os
import sys
import webbrowser
from pathlib import Path

def main():
    """Start the HTTP server for the JavaScript frontend"""
    # Change to the frontend-js directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Configuration
    PORT = 8080
    HOST = 'localhost'
    
    print("🌐 S3 Vector Browser - JavaScript Frontend")
    print("=" * 50)
    print(f"Serving from: {frontend_dir}")
    print(f"URL: http://{HOST}:{PORT}")
    print("Make sure the backend API is running on port 8000")
    print("Start backend with: cd ../backend && python run_api.py")
    print("-" * 50)
    
    # Create HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer((HOST, PORT), handler) as httpd:
            print(f"🚀 Server started at http://{HOST}:{PORT}")
            print("📖 Open the URL above in your browser")
            print("🛑 Press Ctrl+C to stop the server")
            print()
            
            # Optionally open browser
            try:
                webbrowser.open(f"http://{HOST}:{PORT}")
                print("🌐 Opened browser automatically")
            except:
                print("💡 Please open http://localhost:8080 in your browser")
            
            print()
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} is already in use.")
            print(f"💡 Try a different port or stop the process using port {PORT}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()