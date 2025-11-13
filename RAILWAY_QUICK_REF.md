# Railway Deployment Quick Reference

## ✅ Pre-Deployment Checklist

- [ ] All configuration files committed (Procfile, railway.json, nixpacks.toml, runtime.txt)
- [ ] requirements.txt is up to date
- [ ] .gitignore excludes sensitive files (.env, __pycache__, *.pyc)
- [ ] GitHub repository is up to date

## 🚀 Essential Environment Variables

Set these in Railway Dashboard → Variables:

```bash
# Required
FLASK_ENV=production
API_KEYS=your-key-1,your-key-2
RABBITMQ_URL=${{CloudAMQP.CLOUDAMQP_URL}}
REDIS_URL=${{Redis.REDIS_URL}}

# Optional (with defaults)
PORT=5000                      # Railway auto-sets this
DEBUG=false
RATE_LIMIT_PER_MINUTE=100
```

## 📋 Deployment Commands

### Using Railway CLI
```bash
# Install CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open
```

### Using Git (Auto-Deploy)
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
# Railway auto-deploys on push
```

## 🔍 Quick Tests

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

### 2. Send Test Notification
```bash
curl -X POST https://your-app.railway.app/notifications/email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"user_id":"123","template_id":"test","variables":{"name":"Test"}}'
```

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| "No start command found" | Ensure Procfile exists with: `web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 4` |
| "Application Error" | Check logs: `railway logs` |
| "502 Bad Gateway" | Verify app binds to `$PORT`, check start command |
| "RabbitMQ connection failed" | Set `RABBITMQ_URL` or individual variables correctly |
| "Redis timeout" | Use Railway Redis and set `REDIS_URL=${{Redis.REDIS_URL}}` |
| Build fails | Check `runtime.txt` matches Python version in requirements.txt |

## 📊 Monitor Your App

### View Logs
```bash
railway logs --follow
```

### Check Metrics
- Dashboard → Your Service → Metrics
- CPU, Memory, Network usage

### Health Endpoint
```bash
# Should return status of all services
curl https://your-app.railway.app/health
```

## 🔄 Update Deployment

### Code Changes
```bash
git add .
git commit -m "Update feature"
git push origin main
# Auto-deploys
```

### Environment Variables
1. Go to Railway Dashboard
2. Select your service
3. Variables tab
4. Add/Edit/Delete variables
5. Changes apply immediately (may trigger restart)

## 💰 Cost Tracking

- Free tier: $5/month credit
- Monitor usage: Dashboard → Usage
- Optimize:
  - Reduce worker count if low traffic
  - Use sleep mode for dev
  - Share Redis/RabbitMQ instances

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/dashboard
- Full Guide: [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md)
- Railway Docs: https://docs.railway.app
- Support: https://discord.gg/railway

## 📝 Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Set up custom domain (optional)
3. ✅ Configure staging environment
4. ✅ Set up monitoring/alerts
5. ✅ Deploy other microservices (Email, Push, User)
6. ✅ Test end-to-end flow

