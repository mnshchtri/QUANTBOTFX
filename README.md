# 🚀 QuantBotForex - AI-Driven Forex Trading Platform

> **Advanced algorithmic trading platform with AI-powered strategy development, real-time market analysis, and interactive charting capabilities.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

QuantBotForex is a comprehensive algorithmic trading platform that combines advanced technical analysis, AI-driven strategy development, and real-time market data processing. Built with FastAPI backend and React frontend, it provides an intuitive interface for developing, testing, and executing trading strategies.

### 🎯 Key Capabilities

- **Real-time Market Data**: Live forex data from OANDA API
- **AI Strategy Development**: Machine learning-powered strategy creation
- **Interactive Charting**: Advanced charting with Plotly.js
- **Backtesting Engine**: Historical strategy performance analysis
- **Risk Management**: Automated position sizing and risk controls
- **Multi-timeframe Analysis**: Support for M1, M5, M15, H1, H4, D1

## ✨ Features

### 🎯 Core Features

- **📊 Real-time Trading Dashboard**
  - Live market data visualization
  - Interactive candlestick charts
  - Technical indicator overlays
  - Multi-timeframe analysis

- **🤖 AI Strategy Development**
  - Machine learning model integration
  - Automated signal generation
  - Strategy performance metrics
  - Risk-adjusted returns analysis

- **📈 Advanced Charting**
  - Plotly.js powered charts
  - Custom indicator support
  - Drawing tools and annotations
  - Multi-timeframe level management

- **🔄 Backtesting & Replay**
  - Historical data replay
  - Strategy performance testing
  - Interactive replay controls
  - Performance metrics visualization

### 🔧 Technical Features

- **FastAPI Backend**
  - High-performance async API
  - Automatic API documentation
  - WebSocket support for real-time data
  - Comprehensive error handling

- **React Frontend**
  - Modern TypeScript implementation
  - Responsive design
  - Real-time data updates
  - Interactive user interface

- **Data Processing**
  - Pandas for data manipulation
  - Technical indicator calculations
  - Real-time data streaming
  - Historical data management

## 🏗️ Architecture

```
QuantBotForex/
├── backend/                 # FastAPI Backend
│   ├── app.py              # Main application entry
│   ├── routers/            # API route handlers
│   ├── services/           # Business logic services
│   ├── models/             # Pydantic data models
│   └── strategies/         # Trading strategies
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service layer
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
├── config.yaml             # Configuration file
├── requirements.txt         # Python dependencies
└── README.md              # This file
```

## 🚀 Installation

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **OANDA API Key** (for live trading)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/quantbot-forex.git
   cd quantbot-forex
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your OANDA API credentials
   ```

5. **Start the backend**
   ```bash
   cd backend
   python app.py
   ```

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

3. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# OANDA API Configuration
OANDA_API_KEY=your_oanda_api_key_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_BASE_URL=https://api-fxpractice.oanda.com

# Application Settings
APP_ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=sqlite:///./quantbot_forex.db

# Security
SECRET_KEY=your_secret_key_here
```

### Configuration File

The `config.yaml` file contains all application settings:

```yaml
app:
  name: "QuantBotForex"
  version: "2.0.0"
  environment: "development"
  host: "0.0.0.0"
  port: 8000

trading:
  default_instrument: "GBP_JPY"
  default_timeframe: "M15"
  max_position_size: 10000
  risk_percentage: 2.0
```

## 📖 Usage

### Getting Started

1. **Access the Trading Dashboard**
   - Navigate to http://localhost:3000
   - Select your preferred instrument and timeframe
   - View real-time market data

2. **Develop Trading Strategies**
   - Use the Strategy Development panel
   - Configure technical indicators
   - Set risk management parameters

3. **Backtest Strategies**
   - Switch to Replay mode
   - Load historical data
   - Test strategy performance

4. **Monitor Performance**
   - View real-time performance metrics
   - Analyze trade history
   - Track risk-adjusted returns

### API Usage

The backend provides a comprehensive REST API:

```bash
# Get market data
curl http://localhost:8000/api/trading-data/GBP_JPY/M15

# Initialize replay session
curl -X POST http://localhost:8000/replay/initialize \
  -H "Content-Type: application/json" \
  -d '{"instrument": "GBP_JPY", "timeframe": "H1"}'

# Get replay data
curl http://localhost:8000/replay/data
```

## 📚 API Documentation

### Core Endpoints

- **`GET /api/trading-data/{symbol}/{timeframe}`** - Get market data
- **`GET /api/market-info`** - Get market information
- **`POST /replay/initialize`** - Initialize replay session
- **`GET /replay/data`** - Get replay data
- **`POST /replay/control`** - Control replay playback

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠️ Development

### Project Structure

```
backend/
├── app.py                 # FastAPI application
├── routers/              # API route handlers
│   ├── data.py          # Market data endpoints
│   ├── replay.py        # Replay functionality
│   └── strategies.py    # Strategy management
├── services/            # Business logic
│   ├── replay_service.py
│   └── indicator_service.py
├── models/              # Data models
│   ├── trading.py
│   └── replay.py
└── strategies/          # Trading strategies
    └── momentum_following_strategy.py

frontend/
├── src/
│   ├── components/      # React components
│   │   ├── Chart/      # Charting components
│   │   ├── Dashboard/  # Dashboard components
│   │   └── Replay/     # Replay components
│   ├── services/       # API services
│   └── utils/          # Utility functions
└── public/             # Static assets
```

### Development Commands

```bash
# Backend development
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm start

# Run tests
pytest backend/tests/
npm test

# Code formatting
black backend/
npm run format
```

### Adding New Features

1. **Backend Features**
   - Add new routes in `routers/`
   - Implement business logic in `services/`
   - Create data models in `models/`

2. **Frontend Features**
   - Create new components in `src/components/`
   - Add API services in `src/services/`
   - Update routing in `App.tsx`

3. **Trading Strategies**
   - Implement strategies in `strategies/`
   - Extend base strategy class
   - Add strategy configuration

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests for new functionality**
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write comprehensive tests
- Update documentation for new features
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OANDA** for providing market data API
- **FastAPI** for the excellent web framework
- **React** for the frontend framework
- **Plotly.js** for interactive charting
- **Pandas** for data manipulation

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/quantbot-forex/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/quantbot-forex/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/quantbot-forex/wiki)

---

**⭐ Star this repository if you find it helpful!**

**Made with ❤️ by the QuantBotForex Team** 