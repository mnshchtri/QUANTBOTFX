from AlgorithmImports import *

class EmaManager:
    def __init__(self, algorithm, symbol, period = 50,smoothing_factor = 0.5,resolution = None):
        """
        Initializes the EMA Manager.

        :param algorithm: The QCAlgorithm instance
        :param symbol: The trading symbol
        :param period: The EMA period
        :param resolution: The resolution of the EMA
        """
        self.algorithm = algorithm
        self.symbol = symbol

        # Create EMA indicator
        self._ema = self.algorithm.ema(self.symbol, period, smoothing_factor)

    def update(self, time, price):
        """
        Updates the EMA with new price data.

        :param time: The timestamp of the price data
        :param price: The latest price
        """
        self.algorithm.Debug(f"Updating EMA at {time} with price: {price}")
        self._ema.Update(time, price)

    def is_ready(self):
        """
        Checks if the EMA has enough data to be considered ready.

        :return: True if the EMA is ready, otherwise False
        """
        return self._ema.IsReady

    def current_value(self):
        """
        Gets the current value of the EMA.

        :return: The current EMA value
        """
        return self._ema.Current.Value
