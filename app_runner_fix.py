#!/usr/bin/env python3
"""
AWS App Runner optimized entry point for Streamlit application
Fixes common deployment issues with proper startup configuration
"""

import os
import sys
import subprocess

def main():
    # Set required environment variables for App Runner
    os.environ['STREAMLIT_SERVER_PORT'] = '8080'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Launch Streamlit with optimized settings for App Runner
    cmd = [
        'streamlit', 'run', 'app.py',
        '--server.port=8080',
        '--server.address=0.0.0.0',
        '--server.headless=true',
        '--server.enableCORS=false',
        '--server.enableXsrfProtection=false',
        '--browser.gatherUsageStats=false',
        '--server.fileWatcherType=none'
    ]
    
    print("Starting Streamlit application for AWS App Runner...")
    print(f"Command: {' '.join(cmd)}")
    
    # Execute Streamlit
    subprocess.run(cmd)

if __name__ == "__main__":
    main()