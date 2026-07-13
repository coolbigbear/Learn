#!/bin/bash
# deploy.sh — Rebuild frontend, start/restart the production server, and
# expose it via Cloudflare Tunnel.
#
# Usage:
#   ./deploy.sh               — Rebuild + start server + tunnel
#   ./deploy.sh --no-build    — Skip npm build, just start services
#   ./deploy.sh --no-tunnel   — Start server only (no public tunnel)
#   ./deploy.sh status        — Show running services and tunnel URL
#   ./deploy.sh stop          — Stop all services
#
# Prerequisites:
#   - node + npm installed
#   - Python venv at api/.venv/
#   - cloudflared at /opt/data/home/bin/cloudflared

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
API_DIR="$PROJECT_DIR/api"
FRONTEND_DIR="$PROJECT_DIR/frontend"
CLOUDFLARED="/opt/data/home/bin/cloudflared"
TUNNEL_PID_FILE="/tmp/python-tutorials-tunnel.pid"
SERVER_PID_FILE="/tmp/python-tutorials-server.pid"
TUNNEL_URL_FILE="/tmp/python-tutorials-tunnel-url.txt"
PORT="${PORT:-8080}"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

server_pid() { cat "$SERVER_PID_FILE" 2>/dev/null || echo ""; }
tunnel_pid() { cat "$TUNNEL_PID_FILE" 2>/dev/null || echo ""; }

is_running() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

cmd_stop() {
  echo "==> Stopping services..."

  local spid
  spid=$(server_pid)
  if is_running "$spid"; then
    echo "    Stopping server (PID $spid)..."
    kill "$spid" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$SERVER_PID_FILE"

  local tpid
  tpid=$(tunnel_pid)
  if is_running "$tpid"; then
    echo "    Stopping tunnel (PID $tpid)..."
    kill "$tpid" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$TUNNEL_PID_FILE" "$TUNNEL_URL_FILE"

  echo "==> All services stopped."
}

cmd_status() {
  echo "=== Service Status ==="
  local spid tpid
  spid=$(server_pid)
  tpid=$(tunnel_pid)

  if is_running "$spid"; then
    echo "  Server:    RUNNING (PID $spid) — http://localhost:$PORT"
  else
    echo "  Server:    STOPPED"
  fi

  if is_running "$tpid"; then
    echo "  Tunnel:    RUNNING (PID $tpid)"
    if [ -f "$TUNNEL_URL_FILE" ]; then
      url=$(cat "$TUNNEL_URL_FILE")
      echo "  Tunnel URL: $url"
    else
      echo "  Tunnel URL: (not yet available — check logs)"
    fi
  else
    echo "  Tunnel:    STOPPED"
  fi

  echo ""
  echo "  Logs: $LOG_DIR/"
}

cmd_start() {
  echo "==> Starting production server on port $PORT..."

  # Kill any existing server on this port
  local spid
  spid=$(server_pid)
  if is_running "$spid"; then
    echo "    Server already running (PID $spid). Restarting..."
    kill "$spid" 2>/dev/null || true
    sleep 1
  fi

  cd "$API_DIR"

  PRODUCTION=1 nohup uv run python run_prod.py \
    >> "$LOG_DIR/server.log" 2>&1 &
  echo $! > "$SERVER_PID_FILE"

  # Wait for the server to be ready
  echo "    Waiting for server to be ready..."
  for i in $(seq 1 15); do
    if curl -s "http://localhost:$PORT/api/health" > /dev/null 2>&1; then
      echo "    Server is ready at http://localhost:$PORT"
      break
    fi
    if [ "$i" -eq 15 ]; then
      echo "    ERROR: Server failed to start within 15 seconds."
      echo "    Check $LOG_DIR/server.log for details."
      exit 1
    fi
    sleep 1
  done
}

cmd_tunnel() {
  echo "==> Starting Cloudflare Tunnel..."

  local tpid
  tpid=$(tunnel_pid)
  if is_running "$tpid"; then
    echo "    Tunnel already running (PID $tpid). Restarting..."
    kill "$tpid" 2>/dev/null || true
    sleep 1
  fi

  # Start tunnel and capture the URL
  nohup "$CLOUDFLARED" tunnel --url "http://localhost:$PORT" \
    >> "$LOG_DIR/tunnel.log" 2>&1 &
  local new_pid=$!
  echo $new_pid > "$TUNNEL_PID_FILE"

  # Wait for tunnel URL to appear in logs
  echo "    Waiting for tunnel URL..."
  for i in $(seq 1 20); do
    local url
    url=$(grep -oP 'https://[a-zA-Z0-9.-]+\.trycloudflare\.com' "$LOG_DIR/tunnel.log" 2>/dev/null | head -1)
    if [ -n "$url" ]; then
      echo "$url" > "$TUNNEL_URL_FILE"
      echo "    Tunnel is live at: $url"
      break
    fi
    sleep 1
    if [ "$i" -eq 20 ]; then
      echo "    WARNING: Could not detect tunnel URL from logs."
      echo "    Check $LOG_DIR/tunnel.log manually."
    fi
  done
}

cmd_build() {
  echo "==> Building frontend..."
  cd "$FRONTEND_DIR"
  npm install --silent 2>/dev/null
  npm run build
  echo "    Frontend built successfully."
}

# --- Main ---
case "${1:-}" in
  stop)
    cmd_stop
    ;;
  status)
    cmd_status
    ;;
  --no-build)
    cmd_start
    if [ "${2:-}" != "--no-tunnel" ]; then
      cmd_tunnel
    fi
    cmd_status
    ;;
  --no-tunnel)
    cmd_build
    cmd_start
    cmd_status
    ;;
  *)
    cmd_build
    cmd_start
    if [ "${1:-}" != "--no-tunnel" ]; then
      cmd_tunnel
    fi
    cmd_status
    ;;
esac