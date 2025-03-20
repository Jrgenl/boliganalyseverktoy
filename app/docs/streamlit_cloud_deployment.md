# Streamlit Cloud Deployment Guide

This guide explains how to deploy the Boliganalyseverktøy to Streamlit Cloud for permanent hosting.

## Prerequisites

1. A GitHub account
2. The Boliganalyseverktøy code in a GitHub repository
3. A Streamlit Cloud account (can use the same GitHub account)

## Deployment Steps

### 1. Prepare the Repository

1. Create a new GitHub repository for the application
2. Push the application code to the repository
3. Ensure the repository structure is as follows:
   ```
   boliganalyse/
   ├── .streamlit/
   │   └── config.toml
   ├── analysis/
   ├── data/
   ├── scraper/
   ├── tests/
   ├── ui/
   │   ├── web_app.py
   │   ├── config.py
   │   └── utils.py
   ├── utils/
   ├── requirements.txt
   └── README.md
   ```
4. Make sure `requirements.txt` includes all necessary dependencies

### 2. Set Up Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and the main file path (`ui/web_app.py`)
5. Configure advanced settings:
   - Python version: 3.10
   - Packages: Use requirements.txt
   - Secrets: None required for basic functionality

### 3. Deploy the Application

1. Click "Deploy"
2. Wait for the deployment to complete
3. Your app will be available at a URL like: `https://username-appname-streamlit-app.streamlit.app`

### 4. Custom Domain (Optional)

To use a custom domain:

1. Go to your app settings in Streamlit Cloud
2. Under "Custom domain", click "Add domain"
3. Enter your domain name (e.g., boliganalyse.no)
4. Follow the instructions to configure DNS settings with your domain provider
5. Wait for DNS propagation (can take up to 48 hours)

### 5. Continuous Deployment

Streamlit Cloud automatically redeploys your app when you push changes to your GitHub repository. To update the app:

1. Make changes to your code locally
2. Commit and push to GitHub
3. Streamlit Cloud will automatically detect changes and redeploy

## Troubleshooting

If you encounter issues with deployment:

1. Check the deployment logs in Streamlit Cloud
2. Verify all dependencies are correctly listed in requirements.txt
3. Ensure the main file path is correct
4. Check that your code doesn't have any platform-specific dependencies

## Monitoring and Maintenance

1. Streamlit Cloud provides basic monitoring of your app
2. Check the app status regularly
3. Monitor usage and performance
4. Update dependencies periodically to ensure security and stability
