#!/usr/bin/env bash
# QuantBotFX – Start backend (C++) + frontend (React)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
GRN='\033[0;32m'; YLW='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${GRN}[✓]${NC} $*"; }
warn()  { echo -e "${YLW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }
head()  { echo -e "\n${BLU}▶  $*${NC}"; }

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    warn "Shutting down QuantBotFX…"
    [ -n "$BACKEND_PID"  ] && kill "$BACKEND_PID"  2>/dev/null && info "Backend stopped"
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null && info "Frontend stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM

# ── PORT GUARD ────────────────────────────────────────────────────────────────
kill_port() {
    local pid=$(lsof -t -i :"$1")
    if [ -n "$pid" ]; then
        warn "Port $1 is busy (PID $pid) – terminating process…"
        kill -9 "$pid" 2>/dev/null || true
        sleep 1
    fi
}
kill_port 8000
kill_port 3000

# ── DATABASE ──────────────────────────────────────────────────────────────────
head "Verifying Database (Docker)"
if ! docker ps | grep -q quantbot_db; then
    warn "quantbot_db container not running – starting now…"
    docker-compose up -d
fi

# Wait for DB to be ready
for i in $(seq 1 10); do
    if docker exec quantbot_db pg_isready -U quantuser -d quantbot &>/dev/null; then
        info "Database is ready ✓"
        break
    fi
    sleep 1
    [ "$i" -eq 10 ] && warn "Database took too long to start – backend might fail to connect"
done

# ── BACKEND ───────────────────────────────────────────────────────────────────
head "Starting C++ Backend"
BINARY="$ROOT/backend/build/quantbot_backend"

if [ ! -f "$BINARY" ]; then
    warn "Binary not found – building now…"
    bash "$ROOT/build_cpp_backend.sh"
fi

"$BINARY" &
BACKEND_PID=$!
info "Backend PID: $BACKEND_PID"

# Wait for health check (max 10 s)
for i in $(seq 1 10); do
    sleep 1
    if curl -sf http://localhost:8000/health &>/dev/null; then
        info "Backend healthy ✓"
        break
    fi
    [ "$i" -eq 10 ] && warn "Backend health check timed out – check logs"
done

# ── FRONTEND ──────────────────────────────────────────────────────────────────
head "Starting React Frontend"
[ -d "$ROOT/frontend/node_modules" ] || (cd "$ROOT/frontend" && npm install)

cd "$ROOT/frontend"
REACT_APP_API_URL=http://localhost:8000 npm start &
FRONTEND_PID=$!
cd "$ROOT"
info "Frontend PID: $FRONTEND_PID"

# ── STATUS ────────────────────────────────────────────────────────────────────
echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  QuantBotFX  ·  Running                     │"
echo "  │  Backend  →  http://localhost:8000           │"
echo "  │  Frontend →  http://localhost:3000           │"
echo "  │                                              │"
echo "  │  Press Ctrl+C to stop all services           │"
echo "  └─────────────────────────────────────────────┘"
echo ""

wait
