#include "IndicatorCalculator.hpp"
#include <numeric>
#include <cmath>
#include <stdexcept>

namespace quantbot {

// ── Simple Moving Average ─────────────────────────────────────────────────
std::vector<double> IndicatorCalculator::sma(const std::vector<double>& p, int period) {
    std::vector<double> out(p.size(), NAN);
    if ((int)p.size() < period || period <= 0) return out;

    double sum = 0;
    for (int i = 0; i < period; ++i) sum += p[i];
    out[period - 1] = sum / period;

    for (size_t i = period; i < p.size(); ++i) {
        sum += p[i] - p[i - period];
        out[i] = sum / period;
    }
    return out;
}

// ── Exponential Moving Average ────────────────────────────────────────────
std::vector<double> IndicatorCalculator::ema(const std::vector<double>& p, int period) {
    std::vector<double> out(p.size(), NAN);
    if (p.empty() || period <= 0) return out;

    // Seed with first SMA
    if ((int)p.size() < period) return out;
    double seed = 0;
    for (int i = 0; i < period; ++i) seed += p[i];
    out[period - 1] = seed / period;

    double k = 2.0 / (period + 1.0);
    for (size_t i = period; i < p.size(); ++i)
        out[i] = p[i] * k + out[i - 1] * (1.0 - k);

    return out;
}

// ── Relative Strength Index ───────────────────────────────────────────────
std::vector<double> IndicatorCalculator::rsi(const std::vector<double>& p, int period) {
    std::vector<double> out(p.size(), NAN);
    if ((int)p.size() <= period || period <= 0) return out;

    double avg_gain = 0, avg_loss = 0;
    for (int i = 1; i <= period; ++i) {
        double diff = p[i] - p[i - 1];
        if (diff > 0) avg_gain += diff;
        else          avg_loss -= diff;
    }
    avg_gain /= period;
    avg_loss /= period;

    auto rs_to_rsi = [](double g, double l) -> double {
        return l == 0.0 ? 100.0 : 100.0 - 100.0 / (1.0 + g / l);
    };

    out[period] = rs_to_rsi(avg_gain, avg_loss);

    for (size_t i = period + 1; i < p.size(); ++i) {
        double diff = p[i] - p[i - 1];
        double gain = diff > 0 ?  diff : 0;
        double loss = diff < 0 ? -diff : 0;
        avg_gain = (avg_gain * (period - 1) + gain) / period;
        avg_loss = (avg_loss * (period - 1) + loss) / period;
        out[i] = rs_to_rsi(avg_gain, avg_loss);
    }
    return out;
}

// ── MACD Line ─────────────────────────────────────────────────────────────
std::vector<double> IndicatorCalculator::macd_line(const std::vector<double>& p,
                               int fast, int slow) {
    auto fast_ema = ema(p, fast);
    auto slow_ema = ema(p, slow);
    std::vector<double> out(p.size(), NAN);
    for (size_t i = 0; i < p.size(); ++i)
        if (!std::isnan(fast_ema[i]) && !std::isnan(slow_ema[i]))
            out[i] = fast_ema[i] - slow_ema[i];
    return out;
}

} // namespace quantbot
