# AWS Deployment Guide - Streamlit Application

## Overview
This guide covers deploying the AI Blackjack Trainer Streamlit application to AWS using the best service for Python web apps.

## Recommended: AWS App Runner (Best for Streamlit)
AWS App Runner is specifically designed for containerized web applications like Streamlit and provides automatic scaling, load balancing, and GitHub integration.

## Pre-Deployment Steps

### 1. Update GitHub Repository
Ensure your repository includes these new deployment files:
- `amplify.yml` - Build configuration for AWS Amplify
- `Dockerfile` - Container configuration (backup deployment method)
- `AWS_DEPLOYMENT.md` - This deployment guide

### 2. Create requirements.txt
Create a `requirements.txt` file in your repository root with these dependencies:
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
scikit-learn>=1.3.0
requests>=2.31.0
beautifulsoup4>=4.12.0
trafilatura>=1.6.0
Pillow>=10.0.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

## AWS App Runner Deployment Steps

### Step 1: Access AWS App Runner Console
1. Go to [AWS App Runner Console](https://console.aws.amazon.com/apprunner/)
2. Click "Create service"
3. Select "Source code repository"

### Step 2: Connect Repository
1. Select "GitHub" as source
2. Connect to your GitHub account if not already connected
3. Choose repository: `Ali-Haroon3/AIBlackJackTrainer`
4. Choose branch: `main`
5. Select "Automatic" for deployment trigger

### Step 3: Configure Build Settings
1. Runtime: Select "Python 3"
2. Source directory: Leave as root (/)
3. Build command: `pip install -r requirements.txt` (or leave automatic)
4. Start command: `streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true`

### Step 4: Configure Service Settings
1. Service name: `ai-blackjack-trainer`
2. Virtual CPU: 1 vCPU
3. Memory: 2 GB
4. Port: 8080 (App Runner default)
5. Auto scaling: 1-10 instances
6. Health check: Default HTTP settings

### Step 5: Review and Create
1. Review all configurations
2. Click "Create & deploy"
3. Wait for deployment (typically 5-10 minutes)
4. Access your live application URL

## Custom Domain Setup (Optional)
1. Go to "Domain management" in Amplify console
2. Add your custom domain
3. Follow DNS configuration steps
4. Wait for SSL certificate provisioning

## Environment Variables (If Using Database)
Add these in Amplify Environment Variables:
- `DATABASE_URL` - Your PostgreSQL connection string
- `STREAMLIT_SERVER_PORT` - 8501
- `STREAMLIT_SERVER_ADDRESS` - 0.0.0.0

## Monitoring and Maintenance
- Check build logs in Amplify console for any issues
- Monitor application performance in CloudWatch
- Set up automatic deployments on GitHub pushes

## Troubleshooting

### Common Issues:
1. **Build failures**: Check dependency versions in `amplify.yml`
2. **Port conflicts**: Ensure Streamlit runs on port 8501
3. **Memory issues**: Increase build instance size in advanced settings

### Build Timeout Solutions:
- Increase timeout to 30 minutes
- Use build caching for pip dependencies
- Consider pre-built Docker images for faster deployments

## Cost Estimation
- Small traffic (< 1000 visits/month): $1-3/month
- Medium traffic (< 10,000 visits/month): $5-15/month
- Includes hosting, SSL, and basic monitoring

## Resume Description
"Deployed full-stack AI-powered web application on AWS Amplify with automated CI/CD pipeline, featuring real-time data processing, machine learning recommendations, and scalable cloud infrastructure."