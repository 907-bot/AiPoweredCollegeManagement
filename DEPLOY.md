# Deployment Guide — SecureExam Pro

## What goes where

| Part       | Platform       |
|------------|---------------|
| Backend    | Render (Web Service) |
| Database   | Render (PostgreSQL) |
| Redis      | Render (Redis)       |
| Frontend   | GitHub Pages         |

---

## Step 1 — Deploy Backend on Render

### Option A — Auto deploy using render.yaml (Recommended)

1. Go to [render.com](https://render.com) and login with GitHub
2. Click **New → Blueprint**
3. Connect your GitHub repo
4. Render will auto-read `render.yaml` and create all services (API + DB + Redis + Worker)
5. Wait for the deploy to finish (takes about 3-5 minutes first time)
6. Copy your backend URL — looks like `https://secureexam-api.onrender.com`

### Option B — Manual setup

1. Create a **New Web Service** on Render
   - Connect your GitHub repo
   - **Root directory**: leave empty (backend is at root)
   - **Build Command**: `pip install -e .`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python version**: 3.11

2. Create a **PostgreSQL** database (New → PostgreSQL)
   - Name: `secureexam-db`
   - Version: 15
   - Copy the **Internal Connection String**

3. Create a **Redis** instance (New → Redis)
   - Name: `secureexam-redis`
   - Copy the **Internal URL**

4. Go back to your Web Service → **Environment** tab and add:
   ```
   DATABASE_URL    = <PostgreSQL internal connection string>
   REDIS_URL       = <Redis internal URL>
   JWT_SECRET_KEY  = <any long random string>
   ENVIRONMENT     = production
   ```

---

## Step 2 — Configure Frontend

### 2a — Add your backend URL as a GitHub Secret

1. Go to your GitHub repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `NEXT_PUBLIC_API_URL`
4. Value: `https://secureexam-api.onrender.com/api/v1`
   (replace with your actual Render URL)

### 2b — Enable GitHub Pages

1. Go to your GitHub repo → **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. That's it — Pages is now ready

---

## Step 3 — Trigger Frontend Deploy

Push any change to the `client/` folder to main branch:

```bash
git add .
git commit -m "Deploy: configure production API URL"
git push origin main
```

GitHub Actions will automatically build and deploy the frontend.

Your frontend URL will be: `https://<your-username>.github.io/<repo-name>/`

---

## Step 4 — Update CORS on Backend

After you get your GitHub Pages URL, go to Render → your web service → Environment and add:

```
CORS_ORIGINS = https://<your-username>.github.io
```

---

## Verify Everything Works

1. Visit `https://secureexam-api.onrender.com/docs` — you should see the Swagger UI
2. Visit `https://secureexam-api.onrender.com/api/v1/health` — should return `{"status":"healthy",...}`
3. Visit your GitHub Pages URL — login page should load

---

## Bugs Fixed Before This Deploy

| # | File | Bug | Fix |
|---|------|-----|-----|
| 1 | `render.yaml` | `fromService` format was wrong — Render couldn't link DB/Redis | Fixed to use proper `name/type/property` structure |
| 2 | `app/db/database.py` | Render gives `postgres://` but asyncpg needs `postgresql+asyncpg://` | Added URL prefix fixer function |
| 3 | `app/main.py` | DB tables were never created — app crashed on first request | Added `Base.metadata.create_all` in lifespan startup |
| 4 | `.github/workflows/deploy.yml` | `cache: 'client'` is invalid; `NEXT_PUBLIC_API_URL` not passed to build | Fixed cache to `npm`, added env secret in build step |
| 5 | `app/api/routes.py` | `{a.model_dump() for a in answers}` — set of dicts crashes (dicts not hashable) | Changed `{}` to `[]` (list comprehension) |

---

## Cost (Free Tier)

| Service | Free? |
|---------|-------|
| Render Web Service | 750 hrs/month free |
| Render PostgreSQL | Free (90 days, then ~$7/mo) |
| Render Redis | Free |
| GitHub Pages | Free forever |

> Note: On the free tier, Render spins down your backend after 15 minutes of inactivity.
> First request after that takes ~30 seconds to wake up. Upgrade to paid (~$7/mo) to avoid this.
