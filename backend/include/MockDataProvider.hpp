#pragma once
#include "IInterfaces.hpp"
#include <string>
#include <vector>

namespace quantbot {

class MockDataProvider : public IDataProvider {
public:
    std::vector<Candle> get_historical_data(const std::string& symbol, const std::string& timeframe) override;
};

} // namespace quantbot
