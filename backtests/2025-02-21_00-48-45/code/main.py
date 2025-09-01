import debugpy
debugpy.listen(("0.0.0.0", 5678))  # Listening for debugger on port 5678
print("Waiting for debugger to attach...")
debugpy.wait_for_client()  # Pause execution until VS Code connects

from AlgorithmImports import *
from helper import StochRSITrendEvaluator
from FirstHourLogic import FirstTwoHourBreakoutEvaluator
from EmaManager import EmaManager
class GoldBreakoutWithSMA(QCAlgorithm):
    def Initialize(self):
        # Set start date and cash
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2020,3,30)
        self.SetCash(100000)

        # Define symbol
        self.gld = self.AddEquity("GLD", Resolution.Minute).Symbol

        # Create trend evaluators for different timeframes
        self.daily_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Daily)
        self.four_hour_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Hour)
        self.one_hour_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Hour)
        self.fifteen_minute_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Minute)
        self.five_minute_cross = StochRSITrendEvaluator(self,self.gld, resolution = Resolution.Minute) 
        #store value of trend in instance
        self.four_hour_trend = None
        self.one_hour_trend = None 
        self.fifteen_minute_trend = None
        self.daily_breakout_evaluator_confirmation = None
        # initialize  create_consolidators
        self.create_consolidators()

         # Create EMA Manager for 5-minute EMA
        self.ema_manager = EmaManager(self, self.gld,resolution = Resolution.Minute)

        #initialize the trade counter at 0
        self.trade_count = 0
        # schedule to reset trade count to 0 every start of the day
       # schedule to reset trade count to 0 every start of the day
        self.Schedule.On(
    self.DateRules.EveryDay(self.gld),
    self.TimeRules.At(18, 0, TimeZones.NewYork),
    self.reset_trade_count
)

        # Schedule daily evaluation
        self.Schedule.On(
            self.DateRules.EveryDay(self.gld),
            self.TimeRules.At(1, 0),
            self.evaluate_daily_trend
        )

        # Create an instance of the breakout evaluator
        self.daily_breakout_evaluator = FirstTwoHourBreakoutEvaluator(self)

        # define stop loss and take profit 

        self.stop_loss_pips = 2.50  # 250 pips in gold (2.50 in price)
    def OnData(self, data: Slice):
        if self.gld in data.Bars:
            bar = data.Bars[self.gld]
            # You can add logic here for minute-by-minute data processing
    #need to ask bibek if this can have its own class,


       
    def on_fifteen_minute_data(self, sender, bar):
        self.fifteen_minute_trend_evaluator.update(bar.EndTime, bar.Close)
        self.fifteen_minute_trend = self.fifteen_minute_trend_evaluator.evaluate()
        self.Debug(f"15-Minute Trend: {self.fifteen_minute_trend}")

    def evaluate_daily_trend(self):
        # Evaluate the daily trend
        self.Debug(f"Daily Trend: {self.daily_trend_evaluator.evaluate()}")
    def on_one_hour_data(self,sender,bar):
        self.daily_breakout_evaluator_confirmation = self.daily_breakout_evaluator.update_hourly_data(bar)
        self.debug(f"Daily Breakout: {self.daily_breakout_evaluator_confirmation}")
        self.one_hour_trend_evaluator.update(bar.EndTime, bar.Close)
        self.one_hour_trend = self.one_hour_trend_evaluator.evaluate()
    
    def on_five_minute_data(self,sender,bar):
        self.five_minute_cross.update(bar.EndTime, bar.Close)
        self.cross_in_five = self.five_minute_cross.CrossOverUnder()

        if self.trade_count >= 2:
            return

        setup = None  # ✅ Initialize setup with a default value

        if self.daily_breakout_evaluator_confirmation == "BullishBreakConfirmed":
            if (
                self.cross_in_five == "CrossOverDetected"
                and self.fifteen_minute_trend in ["Bullish", "Bullish Continuation"]
                and self.one_hour_trend in ["Bullish", "Bullish Continuation"]
            ):
                setup = "Bull Setup B"
                if self.four_hour_trend in ["Bullish", "Bullish Continuation"]:
                    setup = "Bull Setup A"

        elif self.daily_breakout_evaluator_confirmation == "BearishBreakConfirmed":
            if (
                self.cross_in_five == "CrossOverDetected"
                and self.fifteen_minute_trend in ["Bearish", "Bearish Continuation"]
                and self.one_hour_trend in ["Bearish", "Bearish Continuation"]
            ):
                setup = "Bear Setup B"
                if self.four_hour_trend in ["Bearish", "Bearish Continuation"]:
                    setup = "Bear Setup A"

        if setup:  # ✅ Ensure setup is not None before calling execute_trade
            order_type = "buy" if "Bull" in setup else "sell"
            self.execute_trade(order_type, bar.Close, setup, bar.EndTime)

    def on_four_hour_data(self, sender, bar):
        self.four_hour_trend_evaluator.update(bar.EndTime, bar.Close)
        self.four_hour_trend = self.fifteen_minute_trend_evaluator.evaluate()
        self.Debug(f"four Hour Trend: {self.four_hour_trend}")


    def create_consolidators(self):
        # 4-hour consolidator
        self.four_hour_consolidator = TradeBarConsolidator(timedelta(hours=4))
        self.SubscriptionManager.AddConsolidator(self.gld, self.four_hour_consolidator)
        self.four_hour_consolidator.DataConsolidated += self.on_four_hour_data

        # 1-hour consolidator
        self.one_hour_consolidator = TradeBarConsolidator(timedelta(hours=1))
        self.SubscriptionManager.AddConsolidator(self.gld, self.one_hour_consolidator)
        self.one_hour_consolidator.DataConsolidated += self.on_one_hour_data

        # 15-minute consolidator
        self.fifteen_minute_consolidator = TradeBarConsolidator(timedelta(minutes=15))
        self.SubscriptionManager.AddConsolidator(self.gld, self.fifteen_minute_consolidator)
        self.fifteen_minute_consolidator.DataConsolidated += self.on_fifteen_minute_data
        
        # 5-minute consolidator
        self.five_minute_consolidator = TradeBarConsolidator(timedelta(minutes=5))
        self.SubscriptionManager.AddConsolidator(self.gld, self.five_minute_consolidator)
        self.five_minute_consolidator.DataConsolidated += self.on_five_minute_data
        
    def execute_trade(self, order_type, price, setup, time):
    # Define position size based on setup type
        quantity = 1 if setup in ["Bull Setup B", "Bear Setup B"] else 1.5  

        if order_type == "buy":
        # Market Order (Instant Execution)
            self.MarketOrder(self.gld, quantity)
            self.Debug(f"{setup} - Market BUY executed at {price} on {time}, Quantity: {quantity}")

        # Stop Loss & Take Profit Logic
            stop_loss_price = price - self.stop_loss_pips
            take_profit_multiplier = 2 if setup == "Bull Setup B" else 3
            take_profit_price = price + (self.stop_loss_pips * take_profit_multiplier)

            self.StopMarketOrder(self.gld, -quantity, stop_loss_price)  # Stop Loss
            self.LimitOrder(self.gld, quantity, take_profit_price)  # Take Profit

        elif order_type == "sell":
        # Market Order (Instant Execution)
            self.MarketOrder(self.gld, -quantity)
            self.Debug(f"{setup} - Market SELL executed at {price} on {time}, Quantity: {quantity}")

        # Stop Loss & Take Profit Logic
            stop_loss_price = price + self.stop_loss_pips
            take_profit_multiplier = 2 if setup == "Bear Setup B" else 3
            take_profit_price = price - (self.stop_loss_pips * take_profit_multiplier)

            self.StopMarketOrder(self.gld, quantity, stop_loss_price)  # Stop Loss
            self.LimitOrder(self.gld, -quantity, take_profit_price)  # Take Profit

        self.trade_count += 1

    def reset_trade_count(self):
        self.trade_count = 0
