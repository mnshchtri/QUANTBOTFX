#pragma once
#include <string>
#include <memory>
#include <libpq-fe.h>
#include <nlohmann/json.hpp>

namespace quantbot {

struct User {
    int id;
    std::string username;
    std::string email;
    std::string created_at;
};

class AuthService {
public:
    AuthService(const std::string& conn_str);
    ~AuthService();
    
    void init_db();
    
    nlohmann::json signup(const std::string& username, const std::string& email, const std::string& password);
    nlohmann::json login(const std::string& username, const std::string& password);

private:
    std::string connection_string;
    PGconn* conn = nullptr;
    
    bool connect();
    void disconnect();
    std::string hash_password(const std::string& password);
};

} // namespace quantbot
