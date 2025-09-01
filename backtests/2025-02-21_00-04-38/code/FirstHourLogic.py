# region imports
from AlgorithmImports import *
class FirstTwoHourBreakoutEvaluator:
    def _init_(self, algorithm):
        self.algorithm = algorithm
        self.first_hour_high = None
        self.first_hour_low = None
        self.second_hour_high = None
        self.second_hour_low = None
        self.processed_first_two_hours = False
        self.prev_close_bull = None
        self.prev_close_bear = None
        self.bullish_breakout_in_one_hour = False
        self.bearish_breakout_in_one_hour = False
        # Initialize ⁠ last_processed_date ⁠
        self.last_processed_date = None
    def update_hourly_data(self, bar):
    # Log bar information for debugging
        self.algorithm.Debug(f"Processing bar at {bar.EndTime}. Last Processed Date: {self.last_processed_date}")

    # Detect a new day and reset
        if self.last_processed_date is None or bar.EndTime.date() != self.last_processed_date:
            if not self.algorithm.Securities[bar.Symbol].Exchange.DateIsOpen(bar.EndTime.date()):
                self.algorithm.Debug(f"Skipping non-trading day: {bar.EndTime.date()}")
                return

            self.algorithm.Debug(f"New trading day detected: {bar.EndTime.date()}. Resetting evaluator.")
            self.reset()
            self.last_processed_date = bar.EndTime.date()

    # Add logic to process the hourly data here...


        # Debug first two hours tracking
        self.algorithm.Debug(f"First Hour High: {self.first_hour_high}, Low: {self.first_hour_low}")
        self.algorithm.Debug(f"Second Hour High: {self.second_hour_high}, Low: {self.second_hour_low}")
        self.algorithm.Debug(f"Processed First Two Hours: {self.processed_first_two_hours}")

        # Track the first two hours' high and low
        if not self.processed_first_two_hours and bar.EndTime == 18:
            if self.first_hour_high is None :
                self.first_hour_high = bar.High
                self.first_hour_low = bar.Low
                self.algorithm.Debug("Tracking first hour high and low.")
            elif self.second_hour_high is None and bar.EndTime:
                self.second_hour_high = bar.High
                self.second_hour_low = bar.Low
                self.processed_first_two_hours = True
                self.algorithm.Debug("Tracking second hour high and low. Processing completed for first two hours.")

        # Initialize variables for breakout and confirmation
        breakout_result = None
        confirmed_break = None

        # Evaluate breakout conditions after the first two hours
        if self.processed_first_two_hours:
            if not self.bullish_breakout_in_one_hour:
                if bar.Close > self.first_hour_high and bar.High > self.second_hour_high:
                    self.prev_open_bull = bar.Open
                    self.bullish_breakout_in_one_hour = True
                    breakout_result = "BullishBreak"
                    #self.algorithm.Debug(f"Bullish breakout detected at close: {bar.Close}")
            elif not self.bearish_breakout_in_one_hour:
                if bar.Close < self.first_hour_low and bar.Low < self.second_hour_low:
                    self.prev_open_bear = bar.Open
                    self.bearish_breakout_in_one_hour = True
                    breakout_result = "BearishBreak"
                    #self.algorithm.Debug(f"Bearish breakout detected at close: {bar.Close}")
            # Confirm breakout within the next hour
            if self.processed_first_two_hours and self.bullish_breakout_in_one_hour:
                if bar.Close > self.prev_open_bull:
                    confirmed_break = "BullishBreakConfirmed"
                    #self.algorithm.Debug("Bullish breakout confirmed.")
            elif self.processed_first_two_hours and self.bearish_breakout_in_one_hour:

                if bar.Close < self.prev_open_bear:
                    confirmed_break = "BearishBreakConfirmed"
                    #self.algorithm.Debug("Bearish breakout confirmed.")

        return confirmed_break

    def reset(self):
        self.first_hour_high = None
        self.first_hour_low = None
        self.second_hour_high = None
        self.second_hour_low = None
        self.processed_first_two_hours = False
        self.prev_close_bull = None
        self.prev_close_bear = None
        self.bullish_breakout_in_one_hour = False
        self.bearish_breakout_in_one_hour = False
        self.algorithm.Debug("Evaluator reset for a new day.")
