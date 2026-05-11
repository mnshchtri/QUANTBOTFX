#pragma once
#include "IInterfaces.hpp"
#include <memory>
#include <map>

namespace quantbot {

class TradingService : public ITradingService {
public:
    TradingService(std::shared_ptr<IDataProvider> dp, std::shared_ptr<IIndicatorCalculator> ic);
    
    TradeResult execute_trade(const std::string& symbol, const std::string& side, double volume, double price) override;
    bool close_position(const std::string& id) override;
    std::vector<Position> get_positions() const override;
    AccountSummary get_account() const override;

private:
    std::shared_ptr<IDataProvider> m_data;
    std::shared_ptr<IIndicatorCalculator> m_calc;
    std::map<std::string, Position> m_positions;
    AccountSummary m_account;
    int m_id_counter = 0;

    std::string next_id();
    void recalc_account();
};

} // namespace quantbot
