# QuantBotFX

**High-performance algorithmic trading terminal** — C++17 backend · React/TypeScript frontend.

---

## Architecture

```
QUANTBOTFX/
├── backend/                   # Pure C++17 – no Python
│   ├── include/
│   │   ├── Models.hpp         # Domain structs (Candle, Position, TradeResult…)
│   │   ├── IInterfaces.hpp    # Abstract interfaces (SOLID)
│   │   └── ReplayEngine.hpp   # Stateful candle-replay state machine
│   ├── src/
│   │   ├── IndicatorCalculator.cpp   # SMA · EMA · RSI · MACD
│   │   ├── MockDataProvider.cpp      # Seeded deterministic FX data
│   │   └── TradingService.cpp        # Position mgmt · live PnL
│   ├── main.cpp               # Crow HTTP server · all REST routes
│   └── CMakeLists.txt         # CMake build (auto-fetches Crow + JSON)
│
├── frontend/                  # React 18 · TypeScript · Tailwind · Framer Motion
│   └── src/
│       ├── services/
│       │   ├── api.ts                # Central typed API client
│       │   ├── replayService.ts      # Replay polling helpers
│       │   └── tradingLevelsService.ts
│       ├── components/
│       │   ├── Chart/                # TradingView-style candlestick chart
│       │   ├── Dashboard/            # Watchlist · Indicators · Levels · News
│       │   ├── Layout/               # Sidebar · Header (live account HUD)
│       │   └── Replay/               # Step/play/seek replay interface
│       └── App.tsx
│
├── build_cpp_backend.sh       # One-shot C++ build
└── start.sh                   # Build (if needed) + run backend + frontend
```

---

## REST API  (port 8000)

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Liveness check |
| GET | `/api/candles/:symbol/:tf` | OHLCV candles |
| GET | `/api/indicators/:symbol/:tf` | SMA20 · EMA50 · RSI14 · MACD |
| GET | `/api/trading/summary` | Account balance / equity / PnL |
| GET | `/api/trading/positions` | Open positions |
| POST | `/api/trading/execute` | Place order `{symbol,type,volume,price}` |
| POST | `/api/trading/close/:id` | Close position |
| GET | `/api/replay/initialize/:symbol/:tf` | Load candles into replay engine |
| GET | `/api/replay/status` | Replay state machine status |
| GET | `/api/replay/data` | Current candle window |
| POST | `/api/replay/control` | `{action,value}` – play/pause/step/seek/speed |

---

## Quick Start

### Prerequisites
```bash
brew install cmake          # macOS
# or: sudo apt install cmake  # Ubuntu/Debian
```

### Build & Run
```bash
git clone <repo>
cd QUANTBOTFX

# Build C++ backend (first time ~2 min — downloads Crow + nlohmann/json)
./build_cpp_backend.sh

# Start everything
./start.sh
```

- **Backend** → http://localhost:8000  
- **Frontend** → http://localhost:3000

### Frontend only (backend already running)
```bash
cd frontend && npm install && npm start
```

---

## Development

### C++ Hot Rebuild
```bash
cmake --build backend/build -j$(nproc)
```

### Frontend Dev Server
```bash
cd frontend && REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend HTTP | [Crow](https://crowcpp.org) v1.2 (C++17) |
| JSON | [nlohmann/json](https://github.com/nlohmann/json) v3.11 |
| Frontend | React 18 · TypeScript · Tailwind CSS |
| Animations | Framer Motion |
| Icons | Lucide React · Heroicons |
| Build | CMake 3.14+ · npm |