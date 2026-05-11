#include "TradingService.hpp"
#include <map>
#include <chrono>
#include <sstream>
#include <iomanip>

namespace quantbot {

TradingService::TradingService(std::shared_ptr<IDataProvider> dp,
                               std::shared_ptr<IIndicatorCalculator> ic)
    : m_data(dp), m_calc(ic) {}

std::string TradingService::next_id() {
    std::ostringstream ss;
    ss << "pos_" << std::setw(4) << std::setfill('0') << ++m_id_counter;
    return ss.str();
}

void TradingService::recalc_account() {
    double total_pnl = 0;
    int open = 0;
    for (auto& [id, pos] : m_positions) {
        if (pos.status == "open") {
            total_pnl += pos.pnl;
            ++open;
        }
    }
    m_account.equity     = m_account.balance + total_pnl;
    m_account.pnl_today  = total_pnl;
    m_account.pnl_percent = (m_account.balance != 0) ? (total_pnl / m_account.balance * 100.0) : 0.0;
    m_account.open_trades = open;
}

// ── Execute Trade ─────────────────────────────────────────────────────────
TradeResult TradingService::execute_trade(const std::string& symbol,
                           const std::string& side,
                           double volume,
                           double price) {
    if (volume <= 0 || price <= 0)
        return {false, "Invalid volume or price", ""};

    std::string id = next_id();
    Position pos;
    pos.id            = id;
    pos.symbol        = symbol;
    pos.side          = side;
    pos.volume        = volume;
    pos.entry_price   = price;
    pos.current_price = price;
    pos.pnl           = 0.0;
    pos.status        = "open";

    m_positions[id] = pos;
    recalc_account();

    return {true, "Order filled: " + side + " " + symbol + " @ " + std::to_string(price), id};
}

// ── Close Position ────────────────────────────────────────────────────────
bool TradingService::close_position(const std::string& id) {
    auto it = m_positions.find(id);
    if (it == m_positions.end()) return false;
    it->second.status = "closed";
    m_account.balance += it->second.pnl;
    recalc_account();
    return true;
}

// ── Queries ───────────────────────────────────────────────────────────────
std::vector<Position> TradingService::get_positions() const {
    std::vector<Position> out;
    for (auto& [id, pos] : m_positions)
        if (pos.status == "open") out.push_back(pos);
    return out;
}

AccountSummary TradingService::get_account() const { return m_account; }

} // namespace quantbot
