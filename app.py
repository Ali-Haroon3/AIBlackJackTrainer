#!/usr/bin/env python3
"""
AWS-optimized entry point for the Blackjack AI Training Application
"""

from simple_complete_app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)