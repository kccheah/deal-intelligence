# Railway.app Deployment Guide

## Overview
This guide deploys your Deal Intelligence platform to Railway.app in 30 minutes with zero local setup.

**Cost:** $5-10/month (free tier available)  
**Time to Live:** 30 minutes  
**Uptime:** 99.9%

---

## Step 1: Prepare GitHub Repository (5 min)

### Option A: Using GitHub Web Interface (Easiest)

1. Go to https://github.com/new
2. Repository name: `deal-intelligence`
3. Description: `Cross-border deal intelligence and property due diligence platform`
4. Choose **Public** (free tier)
5. Click **Create repository**

6. Now upload all files:
   - Open your repo on GitHub
   - Click **Add file** → **Upload files**
   - Drag all files from `C:\Users\kctm2\iCloudDrive-New\deal-intelligence\` (keep folder structure)
   - Commit with message: "Initial commit: Complete platform"

### Option B: Using Git Commands (Faster)

```bash
cd C:\Users\kctm2\iCloudDrive-New\deal-intelligence

# Initialize Git
git init
git add .
git commit -m "Initial commit: Deal Intelligence platform"

# Add remote (replace YOUR_USERNAME with kccheah)
git remote add origin https://github.com/kccheah/deal-intelligence.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Account (2 min)

1. Go to https://railway.app
2. Click **Sign Up**
3. Connect with GitHub (easiest)
4. Authorize Railway to access your GitHub

---

## Step 3: Deploy to Railway (5 min)

1. On Railway dashboard, click **New Project**
2. Select **Deploy from GitHub repo**
3. Find and select: `deal-intelligence`
4. Railway auto-detects Docker configuration
5. Click **Deploy**

---

## Step 4: Add Environment Variables (5 min)

While Railway is deploying:

1. Go to your Railway project dashboard
2. Click **Variables**
3. Add each variable:

```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
NEWSAPI_KEY=your-newsapi-key-here

SECRET_KEY=your-random-secret-key-here-generate-one

DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]

CORS_ORIGINS=*

DEBUG=false
```

---

## Step 5: Add PostgreSQL Database (5 min)

1. In Railway project, click **Add Service**
2. Select **PostgreSQL**
3. Railway creates a managed database automatically
4. Copy the `DATABASE_URL` from the PostgreSQL service
5. Paste it into the API service variables

---

## Step 6: Verify Deployment (3 min)

Railway will show you:
- **Live URL:** `https://your-project-xyz.railway.app`
- **Status:** Building → Deploying → Running

Once status shows **Running**:

1. Open: `https://your-project-xyz.railway.app/health`
   - Should return `{"status": "ok"}`

2. Open: `https://your-project-xyz.railway.app/docs`
   - Full Swagger API documentation

3. Test an endpoint:
```bash
curl https://your-project-xyz.railway.app/health
```

---

## Step 7: Setup Custom Domain (Optional, 5 min)

1. In Railway dashboard, go to **Settings**
2. Click **Add Custom Domain**
3. Enter your domain: `api.yourdomain.com`
4. Railway provides DNS instructions
5. Update your DNS records and wait 5-10 minutes

---

## Your Live Platform

Once deployed:

- **API Docs:** https://your-project-xyz.railway.app/docs
- **Health Check:** https://your-project-xyz.railway.app/health
- **API Base URL:** https://your-project-xyz.railway.app

### Test Your API:

```bash
# Sign up
curl -X POST https://your-project-xyz.railway.app/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "first_name": "John",
    "last_name": "Doe"
  }'

# List deals
curl https://your-project-xyz.railway.app/deals

# Login
curl -X POST https://your-project-xyz.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

---

## Troubleshooting

### Deployment Fails
- Check Railway logs: Project → Deployments → Click failed deployment
- Common issues: Missing env vars, wrong Docker config
- Solution: Add missing env variables and redeploy

### API Returns 500 Error
- Check logs: Railway → Logs tab
- Likely cause: Missing `ANTHROPIC_API_KEY` or `NEWSAPI_KEY`
- Fix: Verify env variables are set correctly

### Database Connection Error
- Verify `DATABASE_URL` is set
- Railway automatically manages PostgreSQL
- Make sure PostgreSQL service is running

### High Memory Usage
- Railway free tier has limits
- Upgrade to paid plan if hitting limits
- Scale down `numReplicas` in `railway.toml`

---

## Monitoring & Updates

### View Logs
1. Railway Dashboard → Your Project
2. Click **Logs** tab
3. Real-time application logs

### Update Code
1. Push changes to GitHub
2. Railway auto-redeploys when main branch changes
3. No downtime if using multiple replicas

### Scale Your App
1. Railway Dashboard → Settings
2. Increase `numReplicas` for load balancing
3. Add more database storage as needed

---

## Costs

| Item | Cost |
|------|------|
| API Server (Hobby) | Free tier or $5/mo |
| PostgreSQL Database | Free tier or $5/mo |
| Bandwidth | Free tier included |
| Custom Domain | Free (DNS only) |
| **Total** | **~$10-20/month** |

---

## Next Steps After Deployment

1. ✅ Platform is live at `https://your-project-xyz.railway.app`
2. ⏭️ Test all endpoints via `/docs`
3. ⏭️ Build frontend (React) and connect to this API
4. ⏭️ Add payment processing (Stripe)
5. ⏭️ Launch to users

---

**Your Deal Intelligence platform is now production-ready!** 🚀
