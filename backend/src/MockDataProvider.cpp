#include "MockDataProvider.hpp"
#include <ctime>
#include <cmath>

namespace quantbot {

// Generates seeded deterministic price data that resembles real FX behaviour.
std::vector<Candle> MockDataProvider::get_historical_data(const std::string& /*symbol*/,
                                         const std::string& /*timeframe*/) {
    std::vector<Candle> candles;
    candles.reserve(500);

    // Seed price walk around GBPJPY ~190
    double price = 190.0;
    long long ts  = 1715443200LL; // 2024-05-12 00:00 UTC
    const int step  = 900;        // 15 min bars

    // Simple seeded LCG so data is reproducible
    unsigned long seed = 42;
    auto rnd = [&]() -> double {
        seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
        return (double)(seed >> 33) / (double)(1ULL << 31) - 1.0; // [-1, 1]
    };

    for (int i = 0; i < 500; ++i) {
        double change = rnd() * 0.18;  // ~18 pip tick
        double o = price;
        double c = price + change;
        double h = std::max(o, c) + std::abs(rnd()) * 0.12;
        double l = std::min(o, c) - std::abs(rnd()) * 0.12;

        candles.push_back({ts, o, h, l, c, 1000.0 + std::abs(rnd()) * 500});
        price = c;
        ts   += step;
    }
    return candles;
}

} // namespace quantbot
