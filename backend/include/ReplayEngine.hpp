#pragma once
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include "Models.hpp"

namespace quantbot {

class ReplayEngine {
public:
    enum class State { IDLE, PLAYING, PAUSED, ENDED };

private:
    std::vector<Candle> m_data;
    int    m_index          = 0;
    double m_speed          = 1.0;
    State  m_state          = State::IDLE;
    double m_balance        = 100'000.0;
    double m_initial_balance= 100'000.0;
    std::vector<Position> m_trades;

    // Fast lookup: candle-index → signals/trades
    std::map<int, std::vector<std::string>> m_signal_map;

public:
    // ── Load ─────────────────────────────────────────────────────────────────
    void load(const std::vector<Candle>& candles) {
        m_data    = candles;
        m_index   = 0;
        m_state   = State::PAUSED;
        m_trades.clear();
        m_signal_map.clear();
    }

    bool has_data() const { return !m_data.empty(); }

    // ── Playback controls ─────────────────────────────────────────────────────
    void play()  { if (has_data()) m_state = State::PLAYING; }
    void pause() { m_state = State::PAUSED; }
    void reset() { m_index = 0; m_state = State::PAUSED; }

    bool step_forward() {
        if (!has_data() || m_index >= (int)m_data.size() - 1) {
            m_state = State::ENDED;
            return false;
        }
        ++m_index;
        return true;
    }

    bool step_backward() {
        if (m_index <= 0) return false;
        --m_index;
        m_state = State::PAUSED;
        return true;
    }

    bool seek(int target_index) {
        if (target_index < 0 || target_index >= (int)m_data.size()) return false;
        m_index = target_index;
        return true;
    }

    void set_speed(double s) { m_speed = std::clamp(s, 0.1, 50.0); }

    // ── Queries ───────────────────────────────────────────────────────────────
    std::vector<Candle> current_window() const {
        if (m_data.empty()) return {};
        return {m_data.begin(), m_data.begin() + m_index + 1};
    }

    Candle current_candle() const {
        return m_data.empty() ? Candle{} : m_data[m_index];
    }

    struct Status {
        std::string state;
        int         current_index;
        int         total_candles;
        double      progress_pct;
        double      speed;
        double      balance;
        int         open_trades;
    };

    Status status() const {
        std::string s;
        switch (m_state) {
            case State::IDLE:    s = "idle";    break;
            case State::PLAYING: s = "playing"; break;
            case State::PAUSED:  s = "paused";  break;
            case State::ENDED:   s = "ended";   break;
        }
        int total = (int)m_data.size();
        double pct = total > 0 ? (double)m_index / (total - 1) * 100.0 : 0.0;
        int open = 0;
        for (auto& p : m_trades) if (p.status == "open") ++open;
        return {s, m_index, total, pct, m_speed, m_balance, open};
    }

    // ── Performance ──────────────────────────────────────────────────────────
    double pnl() const { return m_balance - m_initial_balance; }
};

} // namespace quantbot
