#pragma once
#include "Models.hpp"
#include "IInterfaces.hpp"
#include <vector>

namespace quantbot {

class IndicatorCalculator : public IIndicatorCalculator {
public:
    std::vector<double> sma(const std::vector<double>& prices, int period) override;
    std::vector<double> ema(const std::vector<double>& prices, int period) override;
    std::vector<double> rsi(const std::vector<double>& prices, int period) override;
    std::vector<double> macd_line(const std::vector<double>& prices, int fast = 12, int slow = 26) override;
};

} // namespace quantbot
