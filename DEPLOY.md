# Deployment Guide

## Overview

This guide covers deploying:
- **Backend**: FastAPI on Render.com
- **Frontend**: Next.js on GitHub Pages

---

## Part 1: Backend Deployment (Render.com)

### 1. Prepare the Repository

Push your code to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up/Login with GitHub

### 3. Deploy the Backend

1. Create a **New Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `secureexam-api`
   - **Branch**: `main`
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables:
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string  
   - `JWT_SECRET_KEY`: Generate a secure key

5. Add PostgreSQL (Render managed):
   - Create new PostgreSQL instance
   - Version: 15

6. Add Redis (Render managed):
   - Create new Redis instance
   - Version: 7

### 4. Alternative: Use render.yaml

Simply connect the `render.yaml` file in your repository - Render will auto-detect it.

### 5. Get Your Backend URL

Note your backend URL (e.g., `https://secureexam-api.onrender.com`)

---

## Part 2: Frontend Deployment (GitHub Pages)

### 1. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to **Pages**
3. Source: Select **GitHub Actions**

### 2. Configure Backend URL

Edit `client/lib/api.ts`:
```typescript
const API_BASE = "https://your-backend.onrender.com/api/v1";
```

### 3. Push Changes

```bash
git add .
git commit -m "Configure for production"
git push origin main
```

### 4. Deployment会自动触发

The GitHub Action workflow will:
1. Checkout code
2. Install Node.js dependencies
3. Build Next.js static site
4. Deploy to GitHub Pages

### 5. Get Your Frontend URL

Find it at: `https://<username>.github.io/<repository>/`

---

## Testing

1. Visit your GitHub Pages URL
2. Try logging in with demo credentials
3. Create an exam
4. Test the full flow

---

## Troubleshooting

### Backend Issues

- **Database connection failed**: Check DATABASE_URL格式
- **Redis connection failed**: Verify REDIS_URL
- **502 Bad Gateway**: Check logs in Render dashboard

### Frontend Issues

- **API errors**: Verify BACKEND_URL正确
- **404 on assets**: Check basePath配置
- **CORS errors**: Update CORS_ORIGINS in backend config

---

## Custom Domain (Optional)

### GitHub Pages
1. Go to Settings → Pages
2. Add your custom domain
3. Update DNS records

### Render
1. Go to your service settings
2. Add custom domain
3. Update SSL (automatic)

---

## Security Notes

1. Change `JWT_SECRET_KEY` in production
2. Enable SSL on custom domains
3. Set up regular database backups
4. Monitor usage and costs

---

## Cost Estimate

| Service | Free Tier | Paid |
|---------|----------|------|
| Render Web | 750 hours | ~$25/mo |
| Render DB | Free for small | ~$15/mo |
| GitHub Pages | Free | Free |

Total: ~$40/mo for production use