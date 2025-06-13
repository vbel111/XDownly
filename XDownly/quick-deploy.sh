#!/bin/bash

echo "🚀 Downly Quick Deploy Script"
echo "=============================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}Choose your free deployment platform:${NC}"
echo "1. Railway (Recommended - $5/month credit)"
echo "2. Render (Completely free - 750 hours)"
echo "3. Heroku (1000 hours/month)"
echo "4. Vercel (Serverless - 100GB bandwidth)"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}🚂 Railway Deployment${NC}"
        echo "1. Go to https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'Deploy from GitHub repo'"
        echo "4. Select your Downly repository"
        echo "5. Railway will auto-deploy!"
        echo ""
        echo -e "${YELLOW}💡 Tip: Railway auto-detects Python and uses your requirements.txt${NC}"
        ;;
    2)
        echo -e "${GREEN}🎨 Render Deployment${NC}"
        echo "1. Go to https://render.com"
        echo "2. Sign up with GitHub (no credit card needed)"
        echo "3. Create 'New Web Service'"
        echo "4. Connect your repository"
        echo "5. Build Command: pip install -r requirements.txt"
        echo "6. Start Command: gunicorn app:app"
        echo "7. Click 'Create Web Service'"
        ;;
    3)
        echo -e "${GREEN}🟣 Heroku Deployment${NC}"
        echo "Installing Heroku CLI and deploying..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli"
            exit 1
        fi
        
        echo "Creating Heroku app..."
        APP_NAME="downly-$(date +%s)"
        heroku create $APP_NAME
        
        echo "Setting environment variables..."
        heroku config:set SECRET_KEY=$(openssl rand -base64 32)
        heroku config:set FLASK_ENV=production
        
        echo "Deploying to Heroku..."
        git push heroku main
        
        echo -e "${GREEN}✅ Deployed! Opening your app...${NC}"
        heroku open
        ;;
    4)
        echo -e "${GREEN}▲ Vercel Deployment${NC}"
        echo "Installing Vercel CLI and deploying..."
        
        # Check if npm is installed
        if ! command -v npm &> /dev/null; then
            echo "Please install Node.js and npm first"
            exit 1
        fi
        
        echo "Installing Vercel CLI..."
        npm i -g vercel
        
        echo "Deploying to Vercel..."
        vercel --prod
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment initiated!${NC}"
echo -e "${YELLOW}📖 Check DEPLOY_FREE.md for detailed instructions${NC}"
