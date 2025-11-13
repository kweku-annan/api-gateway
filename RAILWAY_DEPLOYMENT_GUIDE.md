# Railway Deployment Guide

## Overview
This guide explains how to deploy the API Gateway to Railway.app with proper configuration.

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository connected to Railway
- RabbitMQ instance (CloudAMQP or Railway template)
- Redis instance (Railway template or Upstash)

## Configuration Files

### 1. `Procfile`
Defines the process to start your application:
```
web: gunicorn run:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120 --access-logfile - --error-logfile -
```

### 2. `railway.json`
Railway-specific configuration:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn run:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. `nixpacks.toml`
Nixpacks build configuration (Railway's default builder):
```toml
[phases.setup]
nixPkgs = ["python313", "gcc", "postgresql"]

[phases.install]
cmds = ["pip install --upgrade pip", "pip install -r requirements.txt"]

[start]
cmd = "gunicorn run:app --bind 0.0.0.0:$PORT --workers 4 --timeout 120"
```

### 4. `runtime.txt`
Specifies Python version:
```
python-3.13.0
```

## Deployment Steps

### Step 1: Prepare Your Repository

1. Ensure all configuration files are committed:
```bash
git add Procfile railway.json nixpacks.toml runtime.txt .railwayignore
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `api-gateway` repository
5. Railway will automatically detect it's a Python project

### Step 3: Add Redis Service

1. In your Railway project, click "+ New"
2. Select "Database" → "Add Redis"
3. Railway will create a Redis instance and provide connection details

### Step 4: Add RabbitMQ Service

**Option A: Using CloudAMQP (Recommended)**
1. Go to https://www.cloudamqp.com/
2. Sign up for a free plan (Little Lemur - 1M messages/month)
3. Create an instance
4. Copy the AMQP URL

**Option B: Using Railway Template**
1. In your Railway project, click "+ New"
2. Search for "RabbitMQ" template
3. Deploy the template

### Step 5: Configure Environment Variables

In your Railway project settings, add these variables:

#### Required Variables
```bash
# Flask Configuration
FLASK_ENV=production
PORT=5000
DEBUG=false

# API Keys (comma-separated for multiple keys)
API_KEYS=your-production-api-key-here,another-key-here

# RabbitMQ Configuration
RABBITMQ_URL=${{CloudAMQP.CLOUDAMQP_URL}}  # If using CloudAMQP
# OR
RABBITMQ_HOST=${{RabbitMQ.RAILWAY_PRIVATE_DOMAIN}}
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# Redis Configuration (automatically set by Railway Redis)
REDIS_URL=${{Redis.REDIS_URL}}  # Railway provides this
# OR manually:
REDIS_HOST=${{Redis.RAILWAY_PRIVATE_DOMAIN}}
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=${{Redis.REDIS_PASSWORD}}

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# User Service (if deployed)
USER_SERVICE_URL=https://your-user-service.railway.app
```

#### Using Railway's Variable References

Railway allows you to reference variables from other services:
- `${{ServiceName.VARIABLE_NAME}}`
- Example: `${{Redis.REDIS_URL}}`

This automatically connects services without hardcoding URLs.

### Step 6: Deploy

1. Railway will automatically deploy when you push to GitHub
2. Or manually trigger deployment from Railway dashboard
3. Monitor logs in Railway dashboard

### Step 7: Verify Deployment

1. **Check Health Endpoint**
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "API Gateway",
    "timestamp": "2025-11-13T18:45:00Z",
    "checks": {
      "api": "ok",
      "rabbitmq": "ok",
      "redis": "ok"
    }
  }
}
```

2. **Test Notification Endpoint**
```bash
curl -X POST https://your-app.railway.app/notifications/email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-production-api-key-here" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "template_id": "welcome_email",
    "variables": {
      "name": "Test User"
    }
  }'
```

## Troubleshooting

### Issue: "No start command was found"
**Solution:** Ensure `Procfile`, `railway.json`, or `nixpacks.toml` exists with proper start command.

### Issue: "Connection to RabbitMQ failed"
**Solution:** 
1. Check `RABBITMQ_URL` or individual RabbitMQ variables are set correctly
2. Verify RabbitMQ service is running
3. Check if using Railway private networking: `${{RabbitMQ.RAILWAY_PRIVATE_DOMAIN}}`

### Issue: "Redis connection timeout"
**Solution:**
1. Ensure Redis service is running
2. Use Railway's private networking: `${{Redis.RAILWAY_PRIVATE_DOMAIN}}`
3. Check Redis password is set correctly

### Issue: "Application crashes on startup"
**Solution:**
1. Check Railway logs: Dashboard → Deployments → View Logs
2. Common causes:
   - Missing environment variables
   - Invalid API_KEYS format
   - Database connection issues
3. Ensure all required dependencies in `requirements.txt`

### Issue: "502 Bad Gateway"
**Solution:**
1. App might be binding to wrong port
2. Ensure using `$PORT` environment variable (Railway provides this)
3. Check gunicorn command: `--bind 0.0.0.0:$PORT`

## Monitoring

### View Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs
railway logs
```

### Metrics
Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

Access from: Dashboard → Your Service → Metrics

## Scaling

### Horizontal Scaling
Railway supports multiple instances:
1. Go to Settings → Scaling
2. Increase replica count

### Vertical Scaling
Upgrade Railway plan for more resources:
- Starter: 512MB RAM, 1 vCPU
- Developer: 8GB RAM, 8 vCPU

### Gunicorn Workers
Adjust workers in start command:
```bash
# Formula: (2 × CPU cores) + 1
--workers 4  # For 2 CPU cores
```

## Environment-Specific Deployments

### Staging Environment
1. Create new Railway project for staging
2. Use separate branch: `staging`
3. Different environment variables
4. Separate RabbitMQ/Redis instances

### Production Environment
1. Use main branch
2. Enable auto-deployment
3. Set up health checks
4. Configure custom domain

## Custom Domain

1. Go to Settings → Domains
2. Click "Add Domain"
3. Enter your domain: `api.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   CNAME api.yourdomain.com your-app.railway.app
   ```
5. Railway automatically provisions SSL certificate

## Cost Optimization

### Free Tier
- $5 free credits per month
- Enough for development/testing

### Tips to Reduce Costs
1. Use Railway's sleep mode for dev environments
2. Share Redis/RabbitMQ instances across services
3. Optimize worker count
4. Set appropriate timeout values
5. Use CloudAMQP free tier for RabbitMQ

## Security Best Practices

1. **Never commit sensitive data**
   - Use Railway environment variables
   - Add `.env` to `.gitignore`

2. **Rotate API Keys regularly**
   - Update `API_KEYS` environment variable
   - Inform clients of new keys

3. **Use Railway's private networking**
   - Services communicate via private domain
   - Faster and more secure

4. **Enable HTTPS only**
   - Railway provides SSL by default
   - Enforce HTTPS in your application

## CI/CD Integration

Railway automatically deploys when you push to GitHub:

1. Push to main branch → Production deployment
2. Push to staging branch → Staging deployment
3. Pull requests → Preview deployments (optional)

### GitHub Actions (Optional)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- API Gateway Issues: https://github.com/kweku-annan/api-gateway/issues

## Next Steps

1. ✅ Deploy API Gateway
2. ⬜ Deploy Email Service
3. ⬜ Deploy Push Notification Service
4. ⬜ Deploy User Service
5. ⬜ Set up monitoring and alerting
6. ⬜ Configure custom domain
7. ⬜ Set up staging environment

