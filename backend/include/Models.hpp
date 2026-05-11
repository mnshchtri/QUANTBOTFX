#pragma once
#include <string>
#include <vector>

namespace quantbot {

// ── Candle ────────────────────────────────────────────────────────────────────
struct Candle {
    long long timestamp;   // Unix epoch seconds
    double    open;
    double    high;
    double    low;
    double    close;
    double    volume;
};

// ── Position ──────────────────────────────────────────────────────────────────
struct Position {
    std::string id;
    std::string symbol;
    std::string side;          // "buy" | "sell"
    double      volume        = 0.0;
    double      entry_price   = 0.0;
    double      current_price = 0.0;
    double      pnl           = 0.0;
    std::string status        = "open";   // "open" | "closed"
};

// ── Trade Result ──────────────────────────────────────────────────────────────
struct TradeResult {
    bool        success;
    std::string message;
    std::string position_id;
};

// ── Account Summary ───────────────────────────────────────────────────────────
struct AccountSummary {
    double balance      = 100'000.0;
    double equity       = 100'000.0;
    double pnl_today    = 0.0;
    double pnl_percent  = 0.0;
    int    open_trades  = 0;
};

} // namespace quantbot
