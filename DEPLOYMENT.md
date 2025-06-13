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
pip install streamlit pandas numpy plotly scikit-learn pillow requests sqlalchemy psycopg2-binary beautifulsoup4 trafilatura anthropic

# Run the application
streamlit run app.py
```

### Step 3: Cloud Deployment Options

#### Option A: Streamlit Cloud (Recommended - Free)

1. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub repository
   - Branch: `main`
   - Main file path: `app.py`
   - Click "Deploy"

2. **Environment Variables (if needed):**
   - In Streamlit Cloud dashboard, go to "Advanced settings"
   - Add environment variables:
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
echo "web: streamlit run app.py --server.port \$PORT --server.address 0.0.0.0" > Procfile
```

#### Option C: Heroku

1. **Create Procfile:**
```bash
echo "web: streamlit run app.py --server.port \$PORT --server.address 0.0.0.0" > Procfile
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
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080

CMD streamlit run app.py --server.port 8080 --server.address 0.0.0.0
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
streamlit run app.py
```

**Production (with custom port):**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
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
   - Change port in `.streamlit/config.toml` or use `--server.port` flag

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
├── .streamlit/
│   └── config.toml
├── app.py
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