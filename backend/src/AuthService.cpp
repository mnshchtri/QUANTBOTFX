#include "AuthService.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>

namespace quantbot {

AuthService::AuthService(const std::string& conn_str) : connection_string(conn_str) {
    connect();
}

AuthService::~AuthService() {
    disconnect();
}

bool AuthService::connect() {
    if (conn) return true;
    conn = PQconnectdb(connection_string.c_str());
    if (PQstatus(conn) != CONNECTION_OK) {
        std::cerr << "❌ Connection to database failed: " << PQerrorMessage(conn) << std::endl;
        disconnect();
        return false;
    }
    return true;
}

void AuthService::disconnect() {
    if (conn) {
        PQfinish(conn);
        conn = nullptr;
    }
}

void AuthService::init_db() {
    if (!connect()) return;
    
    const char* query = R"(
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    )";
    
    PGresult* res = PQexec(conn, query);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        std::cerr << "❌ Error initializing database: " << PQerrorMessage(conn) << std::endl;
    } else {
        std::cout << "✅ Database initialized (users table checked)" << std::endl;
    }
    PQclear(res);
}

std::string AuthService::hash_password(const std::string& password) {
    std::size_t h = std::hash<std::string>{}(password);
    std::stringstream ss;
    ss << std::hex << h;
    return ss.str();
}

nlohmann::json AuthService::signup(const std::string& username, const std::string& email, const std::string& password) {
    if (!connect()) return {{"success", false}, {"error", "Database connection failed"}};
    
    std::string hashed = hash_password(password);
    const char* params[3] = { username.c_str(), email.c_str(), hashed.c_str() };
    
    PGresult* res = PQexecParams(
        conn,
        "INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3)",
        3, nullptr, params, nullptr, nullptr, 0
    );
    
    nlohmann::json result;
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        result = {{"success", false}, {"error", PQerrorMessage(conn)}};
    } else {
        result = {{"success", true}, {"message", "User created successfully"}};
    }
    
    PQclear(res);
    return result;
}

nlohmann::json AuthService::login(const std::string& username, const std::string& password) {
    if (!connect()) return {{"success", false}, {"error", "Database connection failed"}};
    
    std::string hashed = hash_password(password);
    const char* params[2] = { username.c_str(), hashed.c_str() };
    
    PGresult* res = PQexecParams(
        conn,
        "SELECT id, username, email FROM users WHERE username = $1 AND password_hash = $2",
        2, nullptr, params, nullptr, nullptr, 0
    );
    
    nlohmann::json result;
    if (PQresultStatus(res) != PGRES_TUPLES_OK || PQntuples(res) == 0) {
        result = {{"success", false}, {"error", "Invalid username or password"}};
    } else {
        result = {
            {"success", true},
            {"user", {
                {"id", std::stoi(PQgetvalue(res, 0, 0))},
                {"username", PQgetvalue(res, 0, 1)},
                {"email", PQgetvalue(res, 0, 2)}
            }},
            {"token", "mock-jwt-token-" + std::string(PQgetvalue(res, 0, 0))}
        };
    }
    
    PQclear(res);
    return result;
}

} // namespace quantbot
