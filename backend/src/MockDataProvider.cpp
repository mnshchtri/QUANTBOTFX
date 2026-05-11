#include "MockDataProvider.hpp"
#include <ctime>
#include <cmath>

namespace quantbot {

// Generates seeded deterministic price data that resembles real FX behaviour.
std::vector<Candle> MockDataProvider::get_historical_data(const std::string& symbol,
                                         const std::string& timeframe) {
    std::vector<Candle> candles;
    const int count = 500;
    candles.reserve(count);

    // Map timeframe string to seconds
    int step = 900; // Default M15
    if (timeframe == "M1") step = 60;
    else if (timeframe == "M5") step = 300;
    else if (timeframe == "H1") step = 3600;
    else if (timeframe == "H4") step = 14400;
    else if (timeframe == "D1") step = 86400;

    // Use current time as the anchor for the last candle
    long long now_ts = static_cast<long long>(std::time(nullptr));
    // Align to the timeframe boundary
    long long last_ts = (now_ts / step) * step;
    long long start_ts = last_ts - (static_cast<long long>(count - 1) * step);

    // Seed price based on symbol
    double price = 100.0;
    if (symbol.find("JPY") != std::string::npos) price = 190.0;
    else if (symbol.find("USD") != std::string::npos) price = 1.25;
    else if (symbol.find("EUR") != std::string::npos) price = 1.08;

    // Seed based on symbol hash for consistency per symbol
    unsigned long long seed = 0;
    for (char c : symbol) seed = seed * 31 + c;
    
    auto rnd = [&]() -> double {
        seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
        return (double)(seed >> 33) / (double)(1ULL << 31) - 1.0;
    };

    // Pre-walk to the start time to get a consistent price point
    for (int i = 0; i < 1000; ++i) {
        price += rnd() * 0.1;
    }

    long long current_ts = start_ts;
    for (int i = 0; i < count; ++i) {
        double volatility = 0.15;
        if (price < 2.0) volatility = 0.0005; // FX pairs like EURUSD
        
        double change = rnd() * volatility;
        double o = price;
        double c = price + change;
        double h = std::max(o, c) + std::abs(rnd()) * (volatility * 0.6);
        double l = std::min(o, c) - std::abs(rnd()) * (volatility * 0.6);

        candles.push_back({current_ts, o, h, l, c, 1000.0 + std::abs(rnd()) * 500});
        price = c;
        current_ts += step;
    }

    return candles;
}

} // namespace quantbot
