#!/usr/bin/env python3
"""
Alternative Streamlit runner for AWS App Runner
Uses HTTP polling instead of WebSockets to avoid connection issues
"""

import os
import sys
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import subprocess

class StreamlitProxy:
    def __init__(self):
        self.streamlit_process = None
        
    def start_streamlit(self):
        """Start Streamlit with HTTP-only mode"""
        env = os.environ.copy()
        env.update({
            'STREAMLIT_SERVER_PORT': '8501',
            'STREAMLIT_SERVER_ADDRESS': '127.0.0.1',
            'STREAMLIT_SERVER_HEADLESS': 'true',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
        })
        
        cmd = [
            'streamlit', 'run', 'app.py',
            '--server.port=8501',
            '--server.address=127.0.0.1',
            '--server.headless=true',
            '--browser.gatherUsageStats=false'
        ]
        
        print("Starting Streamlit process...")
        self.streamlit_process = subprocess.Popen(cmd, env=env)
        
        # Wait for Streamlit to start
        time.sleep(10)
        print("Streamlit should be running on localhost:8501")

    def start_proxy(self):
        """Start HTTP proxy on port 8080"""
        import requests
        from http.server import BaseHTTPRequestHandler
        
        class ProxyHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    # Forward GET requests to Streamlit
                    url = f"http://127.0.0.1:8501{self.path}"
                    response = requests.get(url, stream=True)
                    
                    self.send_response(response.status_code)
                    for key, value in response.headers.items():
                        if key.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(key, value)
                    self.end_headers()
                    
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            self.wfile.write(chunk)
                            
                except Exception as e:
                    print(f"Proxy error: {e}")
                    self.send_error(502, "Bad Gateway")
            
            def do_POST(self):
                try:
                    # Forward POST requests to Streamlit
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    
                    url = f"http://127.0.0.1:8501{self.path}"
                    response = requests.post(url, data=post_data, headers=dict(self.headers))
                    
                    self.send_response(response.status_code)
                    for key, value in response.headers.items():
                        if key.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(key, value)
                    self.end_headers()
                    
                    self.wfile.write(response.content)
                    
                except Exception as e:
                    print(f"Proxy POST error: {e}")
                    self.send_error(502, "Bad Gateway")
        
        print("Starting proxy server on port 8080...")
        httpd = HTTPServer(('0.0.0.0', 8080), ProxyHandler)
        httpd.serve_forever()

def main():
    proxy = StreamlitProxy()
    
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=proxy.start_streamlit)
    streamlit_thread.daemon = True
    streamlit_thread.start()
    
    # Start proxy server (blocking)
    proxy.start_proxy()

if __name__ == "__main__":
    main()