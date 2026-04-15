# 🛠️ QuantBotFX Issue Tracker & Roadmap

> **Platform Version**: 2.0.4-STABLE  
> **Environment**: Institutional HUD Mainframe  
> **Last Audit**: 2026-04-15

This document tracks current technical debt, functional gaps, and the development roadmap for the QuantBotFX trading terminal.

---

## 🔴 HIGH PRIORITY: Critical Functional Gaps

### Issue #1: Live OANDA Pricing Stream (Watchlist)
- **Description**: The Market Watchlist currently utilizes high-frequency price simulation (`Math.random()`) to demonstrate HUD interactivity.
- **Required**: Implement WebSocket connection to `stream-fxtrade.oanda.com`.
- **Status**: 🟢 UI Ready | 🔴 Logic Pending

### Issue #2: Strategy Engine Integration (Quant Labs)
- **Description**: The "Backtest Engine" and "AI Optimization" UI in Quant Labs are not yet connected to the Python backend executors.
- **Required**: Link `StrategyDevelopment.tsx` state to `/api/strategy/backtest` and `/api/strategy/optimize`.
- **Status**: 🟢 UI Ready | 🔴 Logic Pending

### Issue #3: Account Equity Synchronization
- **Description**: The Header HUD displays mock balance and equity data.
- **Required**: Fetch real-time account data from the connected OANDA account instead of using mock values in `trading.py`.
- **Status**: 🟡 Mocked Implementation

---

## 🟡 MEDIUM PRIORITY: UI/UX & Platform Polish

### Issue #4: Adaptive HUD Scaling (Responsive Check)
- **Description**: Floating panels are fixed width. On 13" laptops, they overlap the central chart area excessively.
- **Required**: Implement a "Compact HUD" mode that reduces panel width or auto-collapses sidebars on smaller viewports.
- **Status**: 🟡 Responsive (Desktop Only)

### Issue #5: Risk Engine View Implementation
- **Description**: The "Risk Engine" navigation link is active, but the dashboard component is missing.
- **Required**: Create `RiskEngine.tsx` to handle margin-call alerts, maximum drawdown limits, and exposure heatmaps.
- **Status**: 🔴 Not Started

---

## 🟢 LOW PRIORITY: Feature Enhancements

### Issue #6: Historical performance Analysis
- **Description**: Users cannot see past trades or cumulative performance charts.
- **Required**: Implement an "Equity Curve" component and a "Closed Trades" history tab in the bottom overlay.
- **Status**: 🔴 Not Started

### Issue #7: Advanced Charting Toolset
- **Description**: Basic Plotly Pan/Zoom is active, but drawing tools (Trendlines, Fibonacci, etc.) are missing.
- **Required**: Integrate drawing library layer over the Plotly chart.
- **Status**: 🟡 Basic Interaction Only

---

## 🏗️ Technical Debt & Optimization
- [ ] **Plotly Source Maps**: Silence console warnings regarding missing source maps in the production build.
- [ ] **ML Resource Optimization**: Evaluate `tensorflow` memory footprint on local machines when running multiple strategies.
- [ ] **Asset Minification**: Optimize glass-morphic backdrop blurs for low-performance GPUs.
