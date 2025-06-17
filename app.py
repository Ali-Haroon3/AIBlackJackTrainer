#!/usr/bin/env python3
"""
AWS-optimized entry point for the Blackjack AI Training Application
"""

import os
from simple_complete_app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)