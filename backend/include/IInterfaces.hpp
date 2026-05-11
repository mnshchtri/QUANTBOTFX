#pragma once
#include <vector>
#include <string>
#include <memory>
#include "Models.hpp"

namespace quantbot {

// ── Data Provider ─────────────────────────────────────────────────────────────
class IDataProvider {
public:
    virtual ~IDataProvider() = default;
    virtual std::vector<Candle> get_historical_data(
        const std::string& symbol,
        const std::string& timeframe) = 0;
};

// ── Indicator Calculator ──────────────────────────────────────────────────────
class IIndicatorCalculator {
public:
    virtual ~IIndicatorCalculator() = default;
    virtual std::vector<double> sma(const std::vector<double>& prices, int period) = 0;
    virtual std::vector<double> ema(const std::vector<double>& prices, int period) = 0;
    virtual std::vector<double> rsi(const std::vector<double>& prices, int period) = 0;
    virtual std::vector<double> macd_line(const std::vector<double>& prices,
                                          int fast = 12, int slow = 26) = 0;
};

// ── Trading Service ───────────────────────────────────────────────────────────
class ITradingService {
public:
    virtual ~ITradingService() = default;
    virtual TradeResult    execute_trade(const std::string& symbol,
                                         const std::string& side,
                                         double volume,
                                         double price) = 0;
    virtual std::vector<Position> get_positions() const = 0;
    virtual AccountSummary        get_account()   const = 0;
    virtual bool                  close_position(const std::string& id) = 0;
};

} // namespace quantbot
