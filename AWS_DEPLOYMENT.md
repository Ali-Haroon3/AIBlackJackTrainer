# AWS Amplify Deployment Guide

## Overview
This guide will help you deploy the AI Blackjack Trainer application to AWS Amplify using your GitHub repository.

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

## AWS Amplify Deployment Steps

### Step 1: Access AWS Amplify Console
1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click "New App" → "Host web app"
3. Select "GitHub" as your source

### Step 2: Connect Repository
1. Authorize AWS to access your GitHub account
2. Select repository: `Ali-Haroon3/AIBlackJackTrainer`
3. Select branch: `main`
4. Click "Next"

### Step 3: Configure Build Settings
1. App name: `ai-blackjack-trainer`
2. Build specification: Use the provided `amplify.yml` file
3. Advanced settings (if needed):
   - Environment variables for database connections
   - Build timeout: 20 minutes (for ML dependencies)

### Step 4: Review and Deploy
1. Review all settings
2. Click "Save and deploy"
3. Wait for deployment (usually 10-15 minutes)

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