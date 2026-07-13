# Deployment Guide — Interactive Python Tutorials

## Architecture

The app runs as a **single uvicorn process** serving both the REST API and the
built frontend (static files + SPA fallback).

```
                         ┌──────────────────────────┐
  Browser ──► Cloudflare  │  uvicorn :8080            │
  (tunnel)      Tunnel    │  ├── /api/*  ──► FastAPI │
                         │  ├── /assets/* ─► static │
                         │  └── /* ──────► SPA      │
                         │               index.html  │
                         └──────────────────────────┘
```

## Current Live URLs

| Environment | URL | Notes |
|---|---|---|
| **Production** | `https://randy-meetup-filed-ahead.trycloudflare.com` | Ephemeral — changes on tunnel restart |
| **Local (server)** | `http://localhost:8080` | Always available on this machine |
| **Dev (Vite HMR)** | `http://localhost:5173` | Hot-reload dev server |

> **⚠ Tunnel URL note:** The Cloudflare quick tunnel URL is **ephemeral** —
> every time the tunnel process restarts you get a new random
> `.trycloudflare.com` URL. To get the current URL run:
> ```bash
> scripts/deploy.sh status
> ```
> or check `logs/tunnel.log`.

## Quick Start

### Build and deploy (full)

```bash
cd /opt/data/projects/python-tutorials
scripts/deploy.sh
```

This will:
1. Install npm deps and build the frontend (`npm run build`)
2. Start the production server (port 8080)
3. Start the Cloudflare tunnel
4. Print the tunnel URL

### Just start the server (skip tunnel)

```bash
scripts/deploy.sh --no-tunnel
```

### Just start the tunnel (server already running)

```bash
scripts/deploy.sh --no-build --no-tunnel
# then separately:
/opt/data/home/bin/cloudflared tunnel --url http://localhost:8080
```

### Stop everything

```bash
scripts/deploy.sh stop
```

### Check status

```bash
scripts/deploy.sh status
```

## Manual Commands

### Start the production server

```bash
cd api
PRODUCTION=1 uv run python run_prod.py
# or use the venv directly:
PRODUCTION=1 .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### Start the Cloudflare tunnel

```bash
/opt/data/home/bin/cloudflared tunnel --url http://localhost:8080
```

### Rebuild the frontend only

```bash
cd frontend
npm install          # only needed first time / after dep changes
npm run build
```

## Automated Startup (systemd user services)

Services can be installed for auto-start on boot:

```bash
# Install service files (already done once)
ln -sf $PWD/scripts/python-tutorials-api.service ~/.config/systemd/user/
ln -sf $PWD/scripts/python-tutorials-tunnel.service ~/.config/systemd/user/

# Enable and start
systemctl --user daemon-reload
systemctl --user enable python-tutorials-api
systemctl --user enable python-tutorials-tunnel
systemctl --user start python-tutorials-api
systemctl --user start python-tutorials-tunnel

# Check status
systemctl --user status python-tutorials-api
systemctl --user status python-tutorials-tunnel

# View logs
journalctl --user -u python-tutorials-api --follow
journalctl --user -u python-tutorials-tunnel --follow
```

## Persistent Domain (Optional)

The current setup uses Cloudflare **quick tunnels** (no account needed) which
get a new random URL on every restart. For a **permanent** URL:

### Option A: Cloudflare Named Tunnel (free)

1. Create a [free Cloudflare account](https://dash.cloudflare.com/sign-up)
2. Add a domain you own to Cloudflare (or use a free `.tk` / `.cf` domain)
3. Run `cloudflared tunnel login` to authenticate
4. Create and configure a named tunnel:

   ```bash
   /opt/data/home/bin/cloudflared tunnel create python-tutorials
   /opt/data/home/bin/cloudflared tunnel route dns python-tutorials tutorials.yourdomain.com
   ```

5. Create `~/.cloudflared/config.yml`:

   ```yaml
   tunnel: python-tutorials
   credentials-file: /home/hermes/.cloudflared/python-tutorials.json
   ingress:
     - hostname: tutorials.yourdomain.com
       service: http://localhost:8080
     - service: http_status:404
   ```

6. Run: `/opt/data/home/bin/cloudflared tunnel run python-tutorials`

### Option B: Vercel (frontend) + Render (backend)

**Frontend on Vercel:**

1. Install Vercel CLI: `npm install -g vercel`
2. `cd frontend`
3. Build: `npm run build`
4. Deploy: `vercel deploy --prod ./dist`
5. Get your `*.vercel.app` URL

**Backend on Render:**

1. Push the `api/` directory to a GitHub repo
2. Create a new Web Service on [render.com](https://render.com)
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
5. Set environment variable: `PRODUCTION=1`
6. Update `frontend/src/api/client.js` `API_BASE` to point to your Render URL

## Directory Structure (Deployment Files)

```
scripts/
├── deploy.sh                   # Main deploy/stop/status script
├── check_prod.py               # Pre-deployment check script
├── python-tutorials-api.service     # Systemd unit (server)
├── python-tutorials-tunnel.service  # Systemd unit (tunnel)
api/
├── run_prod.py                 # Production entry point
├── main.py                     # FastAPI app (modified for static serving)
logs/
├── server.log                  # uvicorn logs
└── tunnel.log                  # cloudflared tunnel logs
```

## Health Check

```bash
# Server status
curl http://localhost:8080/api/health

# Through the tunnel
curl https://<tunnel-url>/api/health
```

Expected response: `{"status":"ok"}`

## Rebuilding After Changes

```bash
# Full rebuild + deploy
cd /opt/data/projects/python-tutorials
scripts/deploy.sh

# Frontend-only change
cd frontend
npm run build
# Server picks up new files immediately (no restart needed)

# Backend-only change — restart server
scripts/deploy.sh --no-build --no-tunnel  # stop everything
scripts/deploy.sh --no-build              # restart just server + tunnel
```

## Tokens / Secrets

- Auth tokens are stored in `api/tutorials.db` (SQLite). The database file is
  auto-created on first start. No external secrets are needed for the default
  deployment.
- The `.env.example` file in `api/` documents any configurable env vars.
- For Cloudflare Named Tunnel setup, you'll need API tokens from
  https://dash.cloudflare.com/profile/api-tokens.