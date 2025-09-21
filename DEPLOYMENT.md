# ConfigMaster Deployment Guide

## 🚀 Recommended Deployment Strategy

### **Option 1: Railway + Vercel (Recommended)**
- **Frontend**: Vercel (free, optimized for Next.js)
- **Backend**: Railway ($5/month, includes PostgreSQL)
- **Total Cost**: ~$5/month

### **Option 2: Full Railway**
- **All services**: Railway ($10-20/month)
- **Simpler management**: Single platform

## 🚂 Railway Deployment

### 1. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

### 2. Environment Variables (Railway Dashboard)

```bash
OPENAI_API_KEY=your-openai-key
EXA_API_KEY=your-exa-key
FIRECRAWL_API_KEY=your-firecrawl-key
FLASK_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### 3. Railway Services Configuration

The `railway.json` file automatically configures:
- **Backend**: Flask API with PostgreSQL
- **Frontend**: Next.js application
- **Discovery**: AI-powered scanner service
- **Databases**: PostgreSQL + Redis

## 📡 Vercel Frontend Deployment

### 1. Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from frontend directory
cd frontend
vercel --prod
```

### 2. Environment Variables (Vercel Dashboard)

```bash
NEXT_PUBLIC_API_URL=https://your-railway-backend.railway.app
```

## 🐳 Alternative: Docker Deployment

### Railway with Docker

Railway automatically detects and deploys your Docker setup:

```bash
# Railway will use your existing Dockerfiles:
# - backend/Dockerfile
# - frontend/Dockerfile
# - discovery/Dockerfile
```

### Self-hosted with Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🔧 Infrastructure Comparison

| Platform | Cost/Month | Pros | Cons |
|----------|------------|------|------|
| **Railway + Vercel** | $5 | Best performance, easy setup | Two platforms |
| **Railway Only** | $10-20 | Single platform | Frontend not optimized |
| **Vercel + PlanetScale** | $15 | Serverless, fast | Database costs |
| **AWS/GCP** | $30-50 | Enterprise features | Complex setup |
| **Digital Ocean** | $15-25 | Docker-native | Less Next.js optimization |

## 🎯 Production Checklist

### Before Deployment:

- [ ] Set up AI API keys (OpenAI, Exa.ai, Firecrawl)
- [ ] Configure environment variables
- [ ] Set up production database
- [ ] Update CORS settings for production domains
- [ ] Configure CDN for static assets
- [ ] Set up monitoring and logging

### Railway Deployment Steps:

1. **Connect GitHub**: Link your repository
2. **Configure Services**: Railway detects services automatically
3. **Set Environment Variables**: Add AI API keys
4. **Deploy**: Railway handles the rest
5. **Custom Domain**: Add your domain in Railway dashboard

### Vercel Deployment Steps:

1. **Import Project**: Connect GitHub repository (frontend folder)
2. **Configure Build**: Next.js auto-detected
3. **Set Environment Variables**: API URL pointing to Railway
4. **Deploy**: Automatic on every push to main
5. **Custom Domain**: Add domain in Vercel dashboard

## 📊 Monitoring & Scaling

### Railway Features:
- **Auto-scaling**: Based on CPU/Memory usage
- **Metrics**: Built-in monitoring dashboard
- **Logs**: Real-time application logs
- **Health checks**: Automatic service monitoring

### Vercel Features:
- **Analytics**: Page performance metrics
- **Functions**: Serverless API endpoints
- **Edge Network**: Global CDN
- **Preview deployments**: Automatic for PRs

## 🔒 Security Configuration

### Railway Security:
```bash
# Set in Railway dashboard
FLASK_SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
DATABASE_SSL=true
```

### Production Environment:
```bash
# Update Flask configuration
FLASK_ENV=production
DEBUG=False
TESTING=False
```

## 🚀 Quick Start Commands

### Deploy to Railway:
```bash
railway login
railway link charles-sims/config-master
railway up
```

### Deploy Frontend to Vercel:
```bash
cd frontend
vercel --prod
```

### Check Deployment Status:
```bash
railway status
vercel ls
```

Railway is indeed an excellent choice for ConfigMaster - it handles your multi-service architecture beautifully and costs significantly less than traditional cloud providers while providing enterprise-level features.