# Test Files Organization

This directory contains all test files organized by category for easy navigation and maintenance.

## Directory Structure

```
tests/
├── README.md                    # This file
├── oanda/                      # OANDA API tests
│   ├── oanda_with_your_token.py
│   ├── oanda_complete_integration.py
│   ├── oanda_proper_integration.py
│   ├── test_new_oanda_token.py
│   ├── test_new_token.py
│   ├── test_oanda_simple.py
│   ├── test_oanda_v20_correct.py
│   ├── test_oanda_correct_auth.py
│   └── test_oanda_connection.py
├── alternative_data/            # Alternative data source tests
│   ├── test_alternative_data.py
│   └── forex_strategy_alphavantage.py
├── strategies/                  # Strategy tests
│   └── forex_strategy_working.py
└── debug/                      # Debug and troubleshooting
    └── debug_oanda_historical.py
```

## Test Categories

### 1. OANDA Tests (`tests/oanda/`)

**Purpose**: Test OANDA API integration and authentication

**Key Files**:
- `oanda_with_your_token.py` - Comprehensive test using your provided token
- `oanda_complete_integration.py` - Full OANDA REST and Streaming API integration
- `oanda_proper_integration.py` - Proper OANDA integration following official docs
- `test_oanda_v20_correct.py` - V20 API endpoint testing
- `test_oanda_correct_auth.py` - Authentication testing

**Usage**:
```bash
cd tests/oanda
python oanda_with_your_token.py
```

**Current Status**: OANDA servers experiencing issues (520, 404, 502 errors)

### 2. Alternative Data Tests (`tests/alternative_data/`)

**Purpose**: Test alternative data sources when OANDA is unavailable

**Key Files**:
- `test_alternative_data.py` - Test Alpha Vantage and Yahoo Finance
- `forex_strategy_alphavantage.py` - Forex strategy using Alpha Vantage

**Usage**:
```bash
cd tests/alternative_data
python test_alternative_data.py
```

### 3. Strategy Tests (`tests/strategies/`)

**Purpose**: Test trading strategies with different data sources

**Key Files**:
- `forex_strategy_working.py` - Working forex strategy implementation

**Usage**:
```bash
cd tests/strategies
python forex_strategy_working.py
```

### 4. Debug Tests (`tests/debug/`)

**Purpose**: Debug and troubleshoot specific issues

**Key Files**:
- `debug_oanda_historical.py` - Debug historical data fetching

**Usage**:
```bash
cd tests/debug
python debug_oanda_historical.py
```

## Quick Test Commands

### Test OANDA Connection
```bash
cd tests/oanda
python oanda_with_your_token.py
```

### Test Alternative Data Sources
```bash
cd tests/alternative_data
python test_alternative_data.py
```

### Test Strategy
```bash
cd tests/strategies
python forex_strategy_working.py
```

## Current Issues and Solutions

### OANDA Server Issues
- **Problem**: 520, 404, 502 errors from OANDA servers
- **Solution**: Use alternative data sources or wait for OANDA to resolve server issues

### Alternative Data Sources
1. **Alpha Vantage**: Requires API key, limited free tier
2. **Yahoo Finance**: No API key required, rate limited
3. **Synthetic Data**: For testing when real data unavailable

## Environment Variables

Set these for OANDA tests:
```bash
export OANDA_ACCESS_TOKEN="your_token_here"
export OANDA_ACCOUNT_ID="your_account_id"
```

## Troubleshooting

### OANDA Issues
1. Check if OANDA servers are down
2. Verify token permissions
3. Try different environments (practice vs live)
4. Check account status and funding

### Alternative Data Issues
1. Check API key validity
2. Monitor rate limits
3. Verify data availability for requested symbols

## Maintenance

- Keep test files organized by category
- Update README when adding new tests
- Document any new issues or solutions
- Clean up obsolete test files regularly 