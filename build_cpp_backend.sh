#!/usr/bin/env bash
# QuantBotFX – C++ backend build script
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
BUILD="$BACKEND/build"

# ── Colours ───────────────────────────────────────────────────────────────────
GRN='\033[0;32m'; YLW='\033[1;33m'; RED='\033[0;31m'; BLU='\033[0;34m'; NC='\033[0m'
info()  { echo -e "${GRN}[✓]${NC} $*"; }
warn()  { echo -e "${YLW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }
head()  { echo -e "\n${BLU}▶  $*${NC}"; }

# ── Dependency check ──────────────────────────────────────────────────────────
head "Checking dependencies"
command -v cmake &>/dev/null  || error "cmake not found – brew install cmake"
command -v make  &>/dev/null  || error "make not found"

CMAKE_VER=$(cmake --version | head -1 | awk '{print $3}')
info "cmake $CMAKE_VER found"

# ── Configure ─────────────────────────────────────────────────────────────────
head "Configuring (CMake)"
mkdir -p "$BUILD"
cmake -S "$BACKEND" -B "$BUILD" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  2>&1 | tail -10

# ── Build ─────────────────────────────────────────────────────────────────────
head "Compiling ($(nproc 2>/dev/null || sysctl -n hw.ncpu) cores)"
cmake --build "$BUILD" --config Release -j"$(nproc 2>/dev/null || sysctl -n hw.ncpu)"

# ── Done ──────────────────────────────────────────────────────────────────────
BINARY="$BUILD/quantbot_backend"
if [ -f "$BINARY" ]; then
    info "Build successful!"
    info "Binary → $BINARY"
    echo ""
    echo "  Run with:  $BINARY"
    echo "  Or simply: ./start.sh"
else
    error "Build succeeded but binary not found at $BINARY"
fi
