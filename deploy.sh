#!/bin/bash

# ConfigMaster Deployment Script
# Run this after authenticating with Railway and Vercel CLIs

set -e

echo "🚀 Starting ConfigMaster Deployment..."

# Check if authenticated
echo "🔐 Checking authentication..."
railway whoami || { echo "❌ Please run 'railway login' first"; exit 1; }
vercel whoami || { echo "❌ Please run 'vercel login' first"; exit 1; }

echo "✅ Authentication verified!"

# Deploy to Railway (Backend + Database)
echo "🚂 Deploying backend to Railway..."
cd "$(dirname "$0")"

# Link to Railway project or create new one
if ! railway status &>/dev/null; then
    echo "📝 Creating new Railway project..."
    railway new configmaster --name "ConfigMaster Backend"
    railway link
else
    echo "🔗 Using existing Railway project..."
fi

# Set environment variables for Railway
echo "⚙️  Setting Railway environment variables..."
read -s -p "Enter your OpenAI API key: " OPENAI_KEY
echo
read -s -p "Enter your Exa.ai API key: " EXA_KEY
echo
read -s -p "Enter your Firecrawl API key: " FIRECRAWL_KEY
echo

railway vars set OPENAI_API_KEY="$OPENAI_KEY"
railway vars set EXA_API_KEY="$EXA_KEY"
railway vars set FIRECRAWL_API_KEY="$FIRECRAWL_KEY"
railway vars set FLASK_ENV=production
railway vars set PYTHONPATH=/app

# Add PostgreSQL and Redis
echo "🗄️  Adding PostgreSQL and Redis..."
railway add postgresql
railway add redis

# Deploy backend
echo "🚀 Deploying backend..."
railway up

# Get Railway backend URL
RAILWAY_URL=$(railway status --json | jq -r '.services[] | select(.name=="backend") | .url')
echo "✅ Backend deployed to: $RAILWAY_URL"

# Deploy frontend to Vercel
echo "📡 Deploying frontend to Vercel..."
cd frontend

# Configure Vercel project
if ! vercel projects ls | grep -q "configmaster-frontend"; then
    echo "📝 Creating new Vercel project..."
    vercel --prod --yes
else
    echo "🔗 Using existing Vercel project..."
    vercel --prod
fi

# Set environment variables for Vercel
vercel env add NEXT_PUBLIC_API_URL production "$RAILWAY_URL"

echo "✅ Frontend deployed to Vercel!"

# Final status
echo "🎉 ConfigMaster deployment complete!"
echo "📊 Services:"
echo "   Backend:  $RAILWAY_URL"
echo "   Frontend: $(vercel ls --json | jq -r '.[0].url')"
echo ""
echo "🔧 Next steps:"
echo "   1. Configure custom domains (optional)"
echo "   2. Set up monitoring"
echo "   3. Test AI scanner with real API keys"