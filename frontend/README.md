# TrimurtiFX Trading Platform

A modern, professional forex trading platform built with React and FastAPI, featuring real-time charts, technical indicators, and market analysis tools.

## Features

### 🎯 Core Trading Features
- **Real-time Candlestick Charts**: Professional OHLC charts with zoom and pan capabilities
- **Multiple Timeframes**: M1, M5, M15, H1, H4, D1 support
- **Symbol Selection**: Support for major forex pairs (GBP_JPY, EUR_USD, USD_JPY, etc.)
- **Market Data**: Real-time price feeds with high/low/close/open data

### 📊 Technical Analysis
- **Technical Indicators**: 
  - Simple Moving Averages (SMA 20, SMA 50)
  - Exponential Moving Averages (EMA 12, EMA 26)
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - Bollinger Bands (Upper/Lower)
  - Stochastic Oscillator (%K, %D)
- **Interactive Indicator Toggles**: Enable/disable indicators with color-coded display
- **Real-time Indicator Calculations**: Backend-powered technical analysis

### 🎮 Replay & Analysis Tools
- **Chart Replay**: Step through historical data candle by candle
- **Playback Controls**: Play, pause, step forward/backward, reset
- **Speed Control**: 0.25x, 0.5x, 1x, 2x, 4x playback speeds
- **Progress Tracking**: Visual progress bar showing replay position

### 📈 Market Information
- **Live Market Data**: Current price, change, percentage change
- **Price Statistics**: High, low, volume, spread information
- **Real-time Updates**: Auto-refreshing market data every 5 seconds

### 📰 News & Analysis
- **Market News**: Latest forex news and analysis
- **Sentiment Analysis**: Positive/negative/neutral news categorization
- **News Sources**: Multiple financial news sources
- **Time-based Updates**: News refreshes every 5 minutes

### 🎨 User Interface
- **Modern Design**: Clean, professional TradingView-inspired interface
- **Responsive Layout**: Works on desktop and tablet devices
- **Interactive Tooltips**: Detailed price and indicator information on hover
- **Color-coded Data**: Green/red candles, indicator colors, sentiment badges

## Technology Stack

### Frontend
- **React 19**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Recharts**: Professional charting library
- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-friendly interface

### Backend
- **FastAPI**: High-performance Python web framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Technical Analysis**: Custom indicator calculations
- **RESTful API**: Clean API design with proper error handling

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd QuantBotForex
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## API Endpoints

### Trading Data
- `GET /api/trading-data/{symbol}/{timeframe}` - Get OHLC data
- `GET /api/indicators/{symbol}/{timeframe}` - Get technical indicators
- `GET /api/market-info/{symbol}` - Get current market data

### News & Analysis
- `GET /api/news/{symbol}` - Get market news
- `GET /api/symbols` - Get available symbols
- `GET /api/timeframes` - Get available timeframes

### System
- `GET /api/health` - Health check
- `GET /` - API information

## Usage

1. **Select a Symbol**: Choose from available forex pairs
2. **Choose Timeframe**: Select your preferred chart timeframe
3. **Enable Indicators**: Toggle technical indicators on/off
4. **Use Replay Mode**: Step through historical data
5. **Monitor News**: Stay updated with market news and analysis

## Features Comparison with Streamlit

| Feature | Streamlit Version (Deprecated) | React Version (Current) |
|---------|-------------------------------|------------------------|
| Real-time Data | ❌ | ✅ |
| Advanced Charting | Limited | ✅ (TradingView) |
| Modular Indicators | Limited | ✅ |
| Strategy Backtesting | Basic | ✅ |
| REST API | ❌ | ✅ |
| UI Customization | ❌ | ✅ |

> **Note:** The Streamlit version is deprecated. All new features and improvements are in the React + FastAPI version.

## Development

### Project Structure
```
QuantBotForex/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── data_loader.py       # Data loading utilities
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chart/       # Trading chart components
│   │   │   ├── Controls/    # Replay controls
│   │   │   └── Dashboard/   # Market info, indicators, news
│   │   └── App.tsx         # Main application
│   └── package.json        # Node.js dependencies
```

### Key Components
- **TradingChart**: Main candlestick chart with indicators
- **ReplayControls**: Playback controls for historical data
- **MarketInfo**: Real-time market data display
- **IndicatorPanel**: Technical indicator toggles
- **NewsPanel**: Market news and analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
