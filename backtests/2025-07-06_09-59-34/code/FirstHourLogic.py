# region imports
from AlgorithmImports import *


class FirstTwoHourBreakoutEvaluator:
    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.first_hour_high = None
        self.first_hour_low = None
        self.second_hour_high = None
        self.second_hour_low = None
        self.processed_first_two_hours = False
        self.prev_open_bull = None
        self.prev_open_bear = None
        self.bullish_breakout_in_one_hour = False
        self.bearish_breakout_in_one_hour = False
        self.last_processed_date = None

    def update_hourly_data(self, bar):
        # Log bar information for debugging
        self.algorithm.Debug(
            f"Processing bar at {bar.EndTime}. Last Processed Date: {self.last_processed_date}"
        )

        # Detect a new day and reset
        if (
            self.last_processed_date is None
            or bar.EndTime.date() != self.last_processed_date
        ):
            if not self.algorithm.Securities[bar.Symbol].Exchange.DateIsOpen(
                bar.EndTime.date()
            ):
                self.algorithm.Debug(f"Skipping non-trading day: {bar.EndTime.date()}")
                return None

            self.algorithm.Debug(
                f"New trading day detected: {bar.EndTime.date()}. Resetting evaluator."
            )
            self.reset()
            self.last_processed_date = bar.EndTime.date()

        # Track the first two hours' high and low
        current_hour = bar.EndTime.hour

        if not self.processed_first_two_hours:
            if current_hour == 9:  # First hour of trading
                if self.first_hour_high is None:
                    self.first_hour_high = bar.High
                    self.first_hour_low = bar.Low
                else:
                    # Update high/low for the first hour
                    self.first_hour_high = max(self.first_hour_high, bar.High)
                    self.first_hour_low = min(self.first_hour_low, bar.Low)
                self.algorithm.Debug(
                    f"First hour - High: {self.first_hour_high}, Low: {self.first_hour_low}"
                )

            elif current_hour == 10:  # Second hour of trading
                if self.second_hour_high is None:
                    self.second_hour_high = bar.High
                    self.second_hour_low = bar.Low
                else:
                    # Update high/low for the second hour
                    self.second_hour_high = max(self.second_hour_high, bar.High)
                    self.second_hour_low = min(self.second_hour_low, bar.Low)
                self.algorithm.Debug(
                    f"Second hour - High: {self.second_hour_high}, Low: {self.second_hour_low}"
                )

            elif current_hour == 11:  # End of first two hours
                self.processed_first_two_hours = True
                self.algorithm.Debug(
                    "First two hours completed. Starting breakout detection."
                )

        # Evaluate breakout conditions after the first two hours
        confirmed_break = None

        if (
            self.processed_first_two_hours
            and not self.bullish_breakout_in_one_hour
            and not self.bearish_breakout_in_one_hour
        ):
            # Check for bullish breakout
            if bar.Close > self.first_hour_high and bar.High > self.second_hour_high:
                self.prev_open_bull = bar.Open
                self.bullish_breakout_in_one_hour = True
                self.algorithm.Debug(f"Bullish breakout detected at close: {bar.Close}")

            # Check for bearish breakout
            elif bar.Close < self.first_hour_low and bar.Low < self.second_hour_low:
                self.prev_open_bear = bar.Open
                self.bearish_breakout_in_one_hour = True
                self.algorithm.Debug(f"Bearish breakout detected at close: {bar.Close}")

        # Confirm breakout within the next hour
        elif self.bullish_breakout_in_one_hour and self.prev_open_bull is not None:
            if bar.Close > self.prev_open_bull:
                confirmed_break = "BullishBreakConfirmed"
                self.algorithm.Debug("Bullish breakout confirmed.")

        elif self.bearish_breakout_in_one_hour and self.prev_open_bear is not None:
            if bar.Close < self.prev_open_bear:
                confirmed_break = "BearishBreakConfirmed"
                self.algorithm.Debug("Bearish breakout confirmed.")

        return confirmed_break

    def reset(self):
        self.first_hour_high = None
        self.first_hour_low = None
        self.second_hour_high = None
        self.second_hour_low = None
        self.processed_first_two_hours = False
        self.prev_open_bull = None
        self.prev_open_bear = None
        self.bullish_breakout_in_one_hour = False
        self.bearish_breakout_in_one_hour = False
        self.algorithm.Debug("Evaluator reset for a new day.")
