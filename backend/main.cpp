/**
 * QuantBotFX – C++ Backend
 * ========================
 * Web framework : Crow (v1.2)
 * JSON          : nlohmann/json (v3.11)
 * Build         : cmake -S . -B build && cmake --build build -j$(nproc)
 * Run           : ./build/quantbot_backend
 */

#include <crow.h>
#include <nlohmann/json.hpp>
#include <memory>
#include <string>
#include <cmath>

// Domain headers
#include "Models.hpp"
#include "IInterfaces.hpp"
#include "ReplayEngine.hpp"
#include "AuthService.hpp"

// Concrete implementations (headers only)
#include "IndicatorCalculator.hpp"
#include "MockDataProvider.hpp"
#include "TradingService.hpp"

using json = nlohmann::json;

// ── JSON serialisers ──────────────────────────────────────────────────────────
json candle_to_json(const quantbot::Candle& c) {
    return {{"timestamp", c.timestamp},
            {"open",      c.open},
            {"high",      c.high},
            {"low",       c.low},
            {"close",     c.close},
            {"volume",    c.volume}};
}

json position_to_json(const quantbot::Position& p) {
    return {{"id",            p.id},
            {"symbol",        p.symbol},
            {"side",          p.side},
            {"volume",        p.volume},
            {"entry_price",   p.entry_price},
            {"current_price", p.current_price},
            {"pnl",           p.pnl},
            {"status",        p.status}};
}

// ── CORS middleware ───────────────────────────────────────────────────────────
struct CORSMiddleware {
    struct context {};
    void before_handle(crow::request& req, crow::response& res, context&) {
        if (req.method == crow::HTTPMethod::OPTIONS) {
            res.add_header("Access-Control-Allow-Origin",  "*");
            res.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
            res.add_header("Access-Control-Allow-Headers", "Content-Type");
            res.code = 204;
            res.end();
        }
    }
    void after_handle(crow::request&, crow::response& res, context&) {
        res.add_header("Access-Control-Allow-Origin",  "*");
        res.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        res.add_header("Access-Control-Allow-Headers", "Content-Type");
    }
};

// ─────────────────────────────────────────────────────────────────────────────
int main() {
    crow::App<CORSMiddleware> app;

    // ── Services (DI) ─────────────────────────────────────────────────────────
    auto data_provider = std::make_shared<quantbot::MockDataProvider>();
    auto indicator_calc = std::make_shared<quantbot::IndicatorCalculator>();
    auto trading_svc    = std::make_shared<quantbot::TradingService>(
                              data_provider, indicator_calc);
    
    // Auth Service (Postgres connection)
    std::string conn_str = "host=localhost port=5432 dbname=quantbot user=quantuser password=quantpassword";
    auto auth_svc = std::make_shared<quantbot::AuthService>(conn_str);
    auth_svc->init_db();

    quantbot::ReplayEngine replay;

    // ─────────────────────────────────────────────────────────────────────────
    // AUTH
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/auth/signup").methods("POST"_method)
    ([&](const crow::request& req) {
        auto body = json::parse(req.body);
        std::string username = body["username"];
        std::string email = body["email"];
        std::string password = body["password"];
        
        auto result = auth_svc->signup(username, email, password);
        return crow::response(result.dump());
    });

    CROW_ROUTE(app, "/api/auth/login").methods("POST"_method)
    ([&](const crow::request& req) {
        auto body = json::parse(req.body);
        std::string username = body["username"];
        std::string password = body["password"];
        
        auto result = auth_svc->login(username, password);
        return crow::response(result.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // HEALTH
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/health")([]() {
        return crow::response(200, R"({"status":"ok","engine":"C++17"})");
    });

    // ─────────────────────────────────────────────────────────────────────────
    // MARKET DATA  GET /api/candles/:symbol/:timeframe
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/candles/<string>/<string>")
    ([&](const std::string& symbol, const std::string& timeframe) {
        auto candles = data_provider->get_historical_data(symbol, timeframe);
        json arr = json::array();
        for (auto& c : candles) arr.push_back(candle_to_json(c));
        return crow::response(json{{"symbol", symbol},
                                   {"timeframe", timeframe},
                                   {"data", arr}}.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // INDICATORS  GET /api/indicators/:symbol/:timeframe
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/indicators/<string>/<string>")
    ([&](const std::string& symbol, const std::string& timeframe) {
        auto candles = data_provider->get_historical_data(symbol, timeframe);
        std::vector<double> closes;
        closes.reserve(candles.size());
        for (auto& c : candles) closes.push_back(c.close);

        auto sma20  = indicator_calc->sma(closes, 20);
        auto ema50  = indicator_calc->ema(closes, 50);
        auto rsi14  = indicator_calc->rsi(closes, 14);
        auto macd   = indicator_calc->macd_line(closes, 12, 26);

        auto to_arr = [&](const std::vector<double>& v) {
            json a = json::array();
            for (size_t i = 0; i < candles.size(); ++i)
                a.push_back(std::isnan(v[i]) ? nullptr : json(v[i]));
            return a;
        };

        return crow::response(json{
            {"symbol",    symbol},
            {"timeframe", timeframe},
            {"sma_20",    to_arr(sma20)},
            {"ema_50",    to_arr(ema50)},
            {"rsi_14",    to_arr(rsi14)},
            {"macd",      to_arr(macd)}
        }.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // ACCOUNT  GET /api/trading/summary
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/trading/summary")
    ([&]() {
        auto a = trading_svc->get_account();
        return crow::response(json{{"data", {
            {"balance",     a.balance},
            {"equity",      a.equity},
            {"pnl_today",   a.pnl_today},
            {"pnl_percent", a.pnl_percent},
            {"open_trades", a.open_trades}
        }}}.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // POSITIONS  GET /api/trading/positions
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/trading/positions")
    ([&]() {
        auto positions = trading_svc->get_positions();
        json arr = json::array();
        for (auto& p : positions) arr.push_back(position_to_json(p));
        return crow::response(json{{"data", arr}}.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // EXECUTE TRADE  POST /api/trading/execute
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/trading/execute").methods("POST"_method)
    ([&](const crow::request& req) {
        try {
            auto body = json::parse(req.body);
            auto result = trading_svc->execute_trade(
                body.at("symbol").get<std::string>(),
                body.at("type").get<std::string>(),
                body.at("volume").get<double>(),
                body.at("price").get<double>());
            return crow::response(json{
                {"success",     result.success},
                {"message",     result.message},
                {"position_id", result.position_id}
            }.dump());
        } catch (std::exception& e) {
            return crow::response(400, json{{"error", e.what()}}.dump());
        }
    });

    // ─────────────────────────────────────────────────────────────────────────
    // CLOSE POSITION  POST /api/trading/close/:id
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/trading/close/<string>").methods("POST"_method)
    ([&](const std::string& id) {
        bool ok = trading_svc->close_position(id);
        return crow::response(json{{"success", ok}}.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // REPLAY – initialize  GET /api/replay/initialize/:symbol/:timeframe
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/replay/initialize/<string>/<string>")
    ([&](const std::string& symbol, const std::string& timeframe) {
        auto candles = data_provider->get_historical_data(symbol, timeframe);
        replay.load(candles);
        auto s = replay.status();
        return crow::response(json{
            {"success",       true},
            {"symbol",        symbol},
            {"timeframe",     timeframe},
            {"total_candles", s.total_candles}
        }.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // REPLAY – status  GET /api/replay/status
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/replay/status")
    ([&]() {
        auto s = replay.status();
        return crow::response(json{
            {"state",         s.state},
            {"current_index", s.current_index},
            {"total_candles", s.total_candles},
            {"progress_pct",  s.progress_pct},
            {"speed",         s.speed},
            {"balance",       s.balance},
            {"open_trades",   s.open_trades}
        }.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    // REPLAY – control  POST /api/replay/control
    // Body: { "action": "play"|"pause"|"reset"|"step"|"step_back"|"seek",
    //         "value": <int seek target or float speed> }
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/replay/control").methods("POST"_method)
    ([&](const crow::request& req) {
        try {
            auto body   = json::parse(req.body);
            std::string action = body.at("action").get<std::string>();
            bool ok = true;

            if      (action == "play")      replay.play();
            else if (action == "pause")     replay.pause();
            else if (action == "reset")     replay.reset();
            else if (action == "step")      ok = replay.step_forward();
            else if (action == "step_back") ok = replay.step_backward();
            else if (action == "seek")      ok = replay.seek(body.value("value", 0));
            else if (action == "speed")     replay.set_speed(body.value("value", 1.0));
            else return crow::response(400, json{{"error","unknown action"}}.dump());

            auto s = replay.status();
            return crow::response(json{
                {"success", ok},
                {"state",   s.state},
                {"index",   s.current_index}
            }.dump());
        } catch (std::exception& e) {
            return crow::response(400, json{{"error", e.what()}}.dump());
        }
    });

    // ─────────────────────────────────────────────────────────────────────────
    // REPLAY – current data  GET /api/replay/data
    // ─────────────────────────────────────────────────────────────────────────
    CROW_ROUTE(app, "/api/replay/data")
    ([&]() {
        auto window = replay.current_window();
        json arr = json::array();
        for (auto& c : window) arr.push_back(candle_to_json(c));
        auto s = replay.status();
        return crow::response(json{
            {"candles",  arr},
            {"state",    s.state},
            {"index",    s.current_index},
            {"progress", s.progress_pct}
        }.dump());
    });

    // ─────────────────────────────────────────────────────────────────────────
    CROW_LOG_INFO << "QuantBotFX C++ Backend starting on :8000";
    app.port(8000).multithreaded().run();
}
