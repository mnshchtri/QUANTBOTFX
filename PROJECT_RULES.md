# QuantBotForex Project Rules

## 🚫 STRICT RULES (Never Violate)

### 1. NO FAKE/MOCK DATA
- **NEVER create fake data or fallback data**
- **NEVER use mock data generation functions**
- **NEVER implement fallback mechanisms that generate synthetic data**
- If data is unavailable, return proper error responses with appropriate HTTP status codes
- All data must come from real sources (OANDA API, etc.)

### 2. NO DUPLICATE FILES
- **NEVER have duplicate files in different locations**
- **NEVER copy files to multiple directories**
- All strategy files must be located ONLY in `backend/strategies/`
- All services must be located ONLY in `backend/services/`
- All routers must be located ONLY in `backend/routers/`
- Maintain a single source of truth for all code files

### 3. API INTEGRATION REQUIREMENTS
- All files must source indicators from the Indicator AI service
- All files must source data from the Data Management AI service
- No hardcoded API keys or credentials in code
- Use configuration files (`config.yaml`, `.env`) for all external service credentials

## 📁 PROJECT STRUCTURE RULES

### Backend Organization
```
backend/
├── strategies/          # ALL trading strategies go here ONLY
├── services/            # ALL business logic services go here ONLY
├── routers/             # ALL API endpoints go here ONLY
├── core/                # Core functionality and utilities
├── models/              # Data models and schemas
├── utils/               # Utility functions
└── app.py               # Main application entry point
```

### Frontend Organization
```
frontend/
├── src/
│   ├── components/      # React components
│   ├── services/        # API service calls
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Utility functions
```

## 🔧 DEVELOPMENT RULES

### 1. Error Handling
- Always return proper HTTP status codes (401, 404, 500, etc.)
- Provide detailed error messages for debugging
- Log errors appropriately with context
- Never expose internal system details in error responses

### 2. Configuration Management
- Use `config.yaml` as primary configuration source
- Use `.env` for environment-specific variables
- Never hardcode configuration values
- Always validate configuration on startup

### 3. Process Management
- If a port or program is already running, stop and display "app already running"
- Never kill existing processes automatically
- Provide clear status information about running services

### 4. Dependencies
- All Python dependencies must be in `backend/requirements.txt`
- All Node.js dependencies must be in `frontend/package.json`
- Project start command must initialize all required dependencies
- Use virtual environments for Python development

## 🎯 STRATEGY INTEGRATION RULES

### 1. Strategy Location
- All strategies must be in `backend/strategies/`
- Use the Strategy Manager service for all strategy operations
- Never import strategies directly from other locations

### 2. Strategy Execution
- Strategies must integrate with the replay system
- Use the Strategy Manager for activation/deactivation
- Execute strategies on replay data through proper APIs
- Track strategy performance and execution metrics

### 3. Signal Generation
- All trading signals must come from registered strategies
- No hardcoded signal generation
- Signals must be properly formatted and validated
- Integrate signals with the replay chart system

## 📊 DATA HANDLING RULES

### 1. Data Sources
- Primary data source: OANDA API
- No synthetic or generated data
- Proper error handling for API failures
- Data validation and quality checks

### 2. Data Formats
- Use pandas DataFrames for market data
- Standard OHLCV format (Open, High, Low, Close, Volume)
- Proper datetime indexing
- Consistent data types across the system

## 🚀 DEPLOYMENT RULES

### 1. Scripts
- `setup.sh`: Environment setup and dependency installation
- `start.sh`: Application startup and service management
- Both scripts must be executable and properly configured

### 2. Environment
- Always check Python and Node.js version compatibility
- Validate OANDA API configuration before starting
- Create necessary directories and log files
- Provide clear next steps and status information

## 🔍 CODE QUALITY RULES

### 1. Imports
- Use absolute imports within the backend
- No relative imports that cross major directory boundaries
- Import from the correct service locations

### 2. Logging
- Use structured logging with appropriate levels
- Include context in log messages
- Log important operations and errors

### 3. Testing
- Test all API endpoints
- Validate strategy execution
- Test error conditions and edge cases

## 📝 DOCUMENTATION RULES

### 1. Code Documentation
- Document all public functions and classes
- Include type hints for all parameters
- Provide clear examples for complex operations

### 2. API Documentation
- Document all API endpoints
- Include request/response examples
- Document error codes and messages

## ⚠️ VIOLATION CONSEQUENCES

Violating these rules will result in:
1. Code rejection and rollback
2. Required fixes before proceeding
3. Potential system instability
4. Inconsistent behavior across the application

## 🔄 REVIEW PROCESS

Before any code changes:
1. Check for duplicate files
2. Verify no fake data generation
3. Ensure proper file organization
4. Validate import statements
5. Test API endpoints
6. Verify error handling

---

**Remember: These rules ensure code quality, maintainability, and system reliability. Follow them strictly!**
