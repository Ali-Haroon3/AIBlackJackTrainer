# AWS Deployment Guide for Blackjack AI Training Application

## Overview
This Flask-based blackjack training application is configured for deployment on AWS infrastructure through GitHub integration.

## Application Structure
- **Entry Point**: `app.py` - AWS-optimized Flask application launcher
- **Main Application**: `simple_complete_app.py` - Complete blackjack game implementation
- **Templates**: `templates/complete_app.html` - Single-page application interface
- **Dependencies**: Minimal Flask stack for maximum compatibility

## Deployment Files

### app.py
Primary entry point that imports and runs the Flask application with production settings.

### buildspec.yml
AWS CodeBuild configuration file that:
- Sets up Python 3.11 runtime environment
- Installs Flask dependencies (flask, flask-cors, flask-socketio, gunicorn)
- Packages the application for deployment

### Procfile
Process file for Heroku-style deployment that configures Gunicorn WSGI server.

## Dependencies
The application requires only these core packages:
- `flask==3.0.0` - Web framework
- `flask-cors==4.0.0` - Cross-origin resource sharing
- `flask-socketio==5.3.6` - WebSocket support
- `gunicorn==21.2.0` - Production WSGI server

## Features Included
- Complete blackjack game with AI coaching
- Interactive card counting practice
- BJA strategy charts with S17/H17 rules
- Monte Carlo simulation with multiple betting strategies
- Real-time analytics and performance tracking
- Responsive web interface with casino-style graphics

## GitHub Integration
1. Push the repository to GitHub
2. Configure AWS CodeBuild to monitor the repository
3. Set up AWS App Runner or Elastic Beanstalk for automatic deployment
4. The buildspec.yml will handle the build process automatically

## Local Testing
To test locally before deployment:
```bash
python app.py
```

## Environment Configuration
The application uses in-memory session storage and requires no external databases or API keys for basic functionality.

## Deployment Architecture
- **Frontend**: Single-page HTML application with JavaScript
- **Backend**: Flask REST API with JSON responses
- **Storage**: In-memory session management
- **Serving**: Gunicorn WSGI server on configurable port
- **Binding**: 0.0.0.0 for proper AWS networking