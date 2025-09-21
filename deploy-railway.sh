#!/bin/bash

# ConfigMaster Railway Deployment Script
# Deploy backend to Railway first

set -e

echo "🚂 Starting Railway Deployment..."

# Check Railway authentication
echo "🔐 Checking Railway authentication..."
railway whoami || { echo "❌ Please run 'railway login' first"; exit 1; }

echo "✅ Railway authentication verified!"

# Navigate to project root
cd "$(dirname "$0")"

# Create or link Railway project
echo "📝 Setting up Railway project..."
if ! railway status &>/dev/null; then
    echo "Creating new Railway project..."
    railway init --name configmaster
else
    echo "🔗 Using existing Railway project..."
fi

# Set environment variables for Railway
echo "⚙️  Setting Railway environment variables..."
echo "Please enter your API keys (they will be hidden):"

read -s -p "Enter your OpenAI API key: " OPENAI_KEY
echo
read -s -p "Enter your Exa.ai API key (or press Enter to skip): " EXA_KEY
echo
read -s -p "Enter your Firecrawl API key (or press Enter to skip): " FIRECRAWL_KEY
echo

echo "Setting environment variables..."
railway variables --set "OPENAI_API_KEY=$OPENAI_KEY"
if [ ! -z "$EXA_KEY" ]; then
    railway variables --set "EXA_API_KEY=$EXA_KEY"
fi
if [ ! -z "$FIRECRAWL_KEY" ]; then
    railway variables --set "FIRECRAWL_API_KEY=$FIRECRAWL_KEY"
fi

railway variables --set "FLASK_ENV=production"
railway variables --set "PYTHONPATH=/app"
railway variables --set "DEBUG=False"

# Add databases
echo "🗄️  Adding PostgreSQL and Redis..."
railway add -d postgresql || echo "PostgreSQL may already exist"
railway add -d redis || echo "Redis may already exist"

# Deploy backend
echo "🚀 Deploying backend to Railway..."
railway up --detach

# Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Get deployment info
echo "📊 Deployment Status:"
railway status

# Get the URL
RAILWAY_URL=$(railway domain)
echo ""
echo "✅ Backend deployed successfully!"
echo "🌐 Backend URL: https://$RAILWAY_URL"
echo ""
echo "🔧 Next steps:"
echo "1. Complete Vercel authentication: vercel login"
echo "2. Deploy frontend: cd frontend && vercel --prod"
echo "3. Set frontend env var: vercel env add NEXT_PUBLIC_API_URL production https://$RAILWAY_URL"
echo ""
echo "📋 Manual Vercel deployment commands:"
echo "   cd frontend"
echo "   vercel login"
echo "   vercel --prod"
echo "   vercel env add NEXT_PUBLIC_API_URL production https://$RAILWAY_URL"