# Deployment Guide

## How to Add This Project to GitHub and Deploy

### Step 1: Create GitHub Repository

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `blackjack-ai-training`
   - Description: `AI-powered blackjack training application with strategy optimization`
   - Set to Public
   - Don't initialize with README (we already have one)

2. **Initialize and push your local repository:**
```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit: Blackjack AI Training App with BJA strategy charts"

# Add GitHub remote (replace 'yourusername' with your actual GitHub username)
git remote add origin https://github.com/yourusername/blackjack-ai-training.git

# Push to GitHub
git push -u origin main
```

### Step 2: Local Development Setup

**Prerequisites:**
- Python 3.8+
- Git

**Installation:**
```bash
# Clone the repository
git clone https://github.com/yourusername/blackjack-ai-training.git
cd blackjack-ai-training

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Step 3: Cloud Deployment Options

#### Option A: AWS App Runner (Recommended)

1. **Deploy to App Runner:**
   - Go to the AWS App Runner console -> "Create service"
   - Source: your GitHub repository, branch `main`
   - Build: "Use a configuration file" (`apprunner.yaml` is committed)
   - App Runner installs `requirements.txt` and starts
     `gunicorn --bind 0.0.0.0:8000 app:app` on port 8000
   - Health check path: `/health`

2. **Environment Variables (if needed):**
   - In the service's configuration, add:
     - `ANTHROPIC_API_KEY` (for AI features)
     - `DATABASE_URL` (for PostgreSQL)

#### Option B: Railway (Easy, Affordable)

1. **Deploy to Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

2. **Add a Procfile:**
```bash
echo "web: gunicorn --bind 0.0.0.0:\$PORT app:app" > Procfile   # already committed
```

#### Option C: Heroku

1. **Create Procfile:**
```bash
echo "web: gunicorn --bind 0.0.0.0:\$PORT app:app" > Procfile   # already committed
```

2. **Deploy to Heroku:**
```bash
# Install Heroku CLI, then:
heroku create your-app-name
heroku buildpacks:set heroku/python
git push heroku main
```

#### Option D: Google Cloud Run

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-8000} app:app"]
```

2. **Deploy:**
```bash
gcloud run deploy --source .
```

### Step 4: Required Environment Variables

For full functionality, set these environment variables:

**Optional (for enhanced features):**
- `ANTHROPIC_API_KEY`: For AI coaching features
- `DATABASE_URL`: For PostgreSQL database
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`: PostgreSQL connection details

**How to get API keys:**
- **Anthropic API**: Sign up at https://console.anthropic.com/

### Step 5: Running the Application

**Local development:**
```bash
python app.py
```

**Production (with custom port):**
```bash
PORT=8080 gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 app:app
```

### Step 6: Updating the Application

```bash
# Make your changes, then:
git add .
git commit -m "Description of changes"
git push origin main

# For cloud deployments, this will automatically trigger a redeploy
```

### Troubleshooting

**Common Issues:**

1. **Port conflicts:**
   - Set the `PORT` environment variable (defaults to 8000)

2. **Missing dependencies:**
   - Check that all packages are installed: `pip install -r requirements.txt`

3. **Database connection issues:**
   - Verify environment variables are set correctly
   - App will fall back to SQLite if PostgreSQL isn't available

4. **Card images not loading:**
   - Ensure `card_images/` directory exists
   - App will generate fallback cards if images are missing

### File Structure for GitHub

```
blackjack-ai-training/
├── README.md
├── LICENSE
├── .gitignore
├── setup.py
├── DEPLOYMENT.md
├── Dockerfile
├── Procfile
├── apprunner.yaml
├── requirements.txt
├── app.py
├── simple_complete_app.py
├── templates/
│   └── complete_app.html
├── game_engine.py
├── enhanced_ai_coach.py
├── bja_strategy.py
├── bja_charts.py
├── blackjack_table.py
├── card_counting.py
├── card_visuals.py
├── database.py
├── analytics.py
├── user_management.py
├── monte_carlo.py
├── download_cards.py
├── web_scraper.py
├── card_images/           # Downloaded SVG card files
└── attached_assets/       # BJA strategy reference files
```

### Next Steps

1. Star the repository to bookmark it
2. Fork it to contribute improvements
3. Submit issues for bugs or feature requests
4. Share with the blackjack community

The application is now ready for deployment and sharing!