
from AlgorithmImports import *



class StochRSITrendEvaluator:
    #Initiaize the parameter for  stochastic indicator
    def __init__(self, algorithm, symbol, period=14, k_period=3, d_period=3, resolution = None):
        self.algorithm = algorithm
        self.symbol = symbol
        self.stoch_rsi = self.algorithm.srsi(
            self.symbol,
            period,
            period,
            k_period,
            d_period,
        )
        self.previous_k = None
        self.previous_d = None
        self.current_trend = "Neutral"
        self.cross = "Nothing"
    #update the time and price 
    def update(self, time, price):
        self.stoch_rsi.update(time, price)
    # provide the steps to indicate if trend is Bullish Continuation or Bullish
    def evaluate(self):
        if not self.stoch_rsi.is_ready:
            return "Neutral"
        k_value = self.stoch_rsi.k.current.value
        d_value = self.stoch_rsi.d.current.value
        if k_value > d_value and k_value > 20 and d_value > 20:
            if (
                self.previous_k is not None and self.previous_d is not None and
                k_value > 90 and d_value > 90 and self.previous_k > 90 and self.previous_d > 90
            ):
                self.current_trend = "Bullish Continuation"
            else:
                self.current_trend = "Bullish"
        elif k_value < d_value and k_value < 80 and d_value < 80:
            if (
                self.previous_k is not None and self.previous_d is not None and
                k_value < 10 and d_value < 10 and self.previous_k < 10 and self.previous_d < 10
            ):
                self.current_trend = "Bearish Continuation"
            else:
                self.current_trend = "Bearish"
        else:
            self.current_trend = "Neutral"
        self.previous_k = k_value
        self.previous_d = d_value
        return self.current_trend
    #function that dectects crossover or crossunder in stochasticrsi
    def CrossOverUnder(self):
        if not self.stoch_rsi.is_ready:
            return "Neutral"
        k_value = self.stoch_rsi.k.current.value
        d_value = self.stoch_rsi.d.current.value
        if self.previous_k is not None and self.previous_d is not None:
            if self.previous_k < self.previous_d and k_value > d_value:
                self.cross = "CrossOverDetected"
            elif self.previous_k > self.previous_d and k_value < d_value:
                self.cross = "CrossUnderDetected"
        else:
            self.cross = "None"        
        self.previous_k = k_value
        self.previous_d = d_value
        return self.cross
