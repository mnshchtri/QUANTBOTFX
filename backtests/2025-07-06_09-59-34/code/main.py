from AlgorithmImports import *
from helper import StochRSITrendEvaluator
from FirstHourLogic import FirstTwoHourBreakoutEvaluator
from EmaManager import EmaManager
from AISignalGenerator import AISignalGenerator
from datetime import timedelta

class GoldBreakoutWithSMA(QCAlgorithm):
    def Initialize(self):
        # Set start date and cash
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2020,3,30)
        self.SetCash(100000)

        # Define symbol
        self.gld = self.AddEquity("GLD", Resolution.Minute).Symbol

        # Initialize AI Signal Generator
        self.ai_signal_generator = AISignalGenerator(self, self.gld)
        
        # Train AI model with historical data (simplified training)
        self.train_ai_model()
        
        # Create trend evaluators for different timeframes
        self.daily_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Daily)
        self.four_hour_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Hour)
        self.one_hour_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Hour)
        self.fifteen_minute_trend_evaluator = StochRSITrendEvaluator(self, self.gld, resolution=Resolution.Minute)
        self.five_minute_cross = StochRSITrendEvaluator(self,self.gld, resolution = Resolution.Minute) 
        
        # Store value of trend in instance
        self.four_hour_trend = None
        self.one_hour_trend = None 
        self.fifteen_minute_trend = None
        self.daily_breakout_evaluator_confirmation = None
        
        # AI signal storage
        self.ai_signal = "NEUTRAL"
        self.ai_confidence = 0.5
        
        # Initialize create_consolidators
        self.create_consolidators()

        # Create EMA Manager for 5-minute EMA
        self.ema_manager = EmaManager(self, self.gld,resolution = Resolution.Minute)

        # Initialize the trade counter at 0
        self.trade_count = 0
        
        # AI confidence thresholds
        self.min_ai_confidence = 0.7  # Minimum confidence for AI signal
        self.ai_weight = 0.3  # Weight given to AI signal vs technical signals
        
        # Schedule to reset trade count to 0 every start of the day
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

        # Define stop loss and take profit 
        self.stop_loss_pips = 2.50  # 250 pips in gold (2.50 in price)
        
    def train_ai_model(self):
        """Train the AI model with historical data"""
        try:
            # Get historical data for training
            history = self.History(self.gld, 100, Resolution.Minute)
            
            if history is not None and len(history) > 50:
                # Convert to training format
                training_data = []
                for index, row in history.iterrows():
                    training_data.append({
                        'price': row['close'],
                        'volume': row['volume'] if 'volume' in row else 1000
                    })
                
                # Train the model
                self.ai_signal_generator.train_model(training_data)
                self.Debug("AI model trained successfully")
            else:
                self.Debug("Insufficient historical data for AI training")
        except Exception as e:
            self.Debug(f"AI training failed: {str(e)}")

    def OnData(self, data: Slice):
        if self.gld in data.Bars:
            bar = data.Bars[self.gld]
            # Update AI signal generator
            self.ai_signal_generator.update(bar.EndTime, bar.Close, bar.Volume)
            
            # Generate AI signal
            self.ai_signal, self.ai_confidence = self.ai_signal_generator.generate_signal(bar.Close, bar.Volume)
            
            self.Debug(f"AI Signal: {self.ai_signal}, Confidence: {self.ai_confidence:.3f}")

    def on_fifteen_minute_data(self, sender, bar):
        self.fifteen_minute_trend_evaluator.update(bar.EndTime, bar.Close)
        self.fifteen_minute_trend = self.fifteen_minute_trend_evaluator.evaluate()
        self.Debug(f"15-Minute Trend: {self.fifteen_minute_trend}")

    def evaluate_daily_trend(self):
        # Evaluate the daily trend
        self.Debug(f"Daily Trend: {self.daily_trend_evaluator.evaluate()}")
        
    def on_one_hour_data(self,sender,bar):
        self.daily_breakout_evaluator_confirmation = self.daily_breakout_evaluator.update_hourly_data(bar)
        self.Debug(f"Daily Breakout: {self.daily_breakout_evaluator_confirmation}")
        self.one_hour_trend_evaluator.update(bar.EndTime, bar.Close)
        self.one_hour_trend = self.one_hour_trend_evaluator.evaluate()
    
    def on_five_minute_data(self,sender,bar):
        self.five_minute_cross.update(bar.EndTime, bar.Close)
        self.cross_in_five = self.five_minute_cross.CrossOverUnder()

        if self.trade_count >= 2:
            return

        setup = None  # Initialize setup with a default value

        # Enhanced setup logic with AI integration
        if self.daily_breakout_evaluator_confirmation == "BullishBreakConfirmed":
            if (
                self.cross_in_five == "CrossOverDetected"
                and self.fifteen_minute_trend in ["Bullish", "Bullish Continuation"]
                and self.one_hour_trend in ["Bullish", "Bullish Continuation"]
            ):
                # Check AI confirmation
                ai_bullish = (self.ai_signal == "BUY" and self.ai_confidence >= self.min_ai_confidence)
                
                if ai_bullish:
                    setup = "Bull Setup A (AI Enhanced)"
                else:
                    setup = "Bull Setup B"

        elif self.daily_breakout_evaluator_confirmation == "BearishBreakConfirmed":
            if (
                self.cross_in_five == "CrossOverDetected"
                and self.fifteen_minute_trend in ["Bearish", "Bearish Continuation"]
                and self.one_hour_trend in ["Bearish", "Bearish Continuation"]
            ):
                # Check AI confirmation
                ai_bearish = (self.ai_signal == "SELL" and self.ai_confidence >= self.min_ai_confidence)
                
                if ai_bearish:
                    setup = "Bear Setup A (AI Enhanced)"
                else:
                    setup = "Bear Setup B"

        if setup:  # Ensure setup is not None before calling execute_trade
            order_type = "buy" if "Bull" in setup else "sell"
            # Adjust position size based on AI confidence
            position_multiplier = 1.5 if "AI Enhanced" in setup else 1.0
            self.execute_trade(order_type, bar.Close, setup, bar.EndTime, position_multiplier)

    def on_four_hour_data(self, sender, bar):
        self.four_hour_trend_evaluator.update(bar.EndTime, bar.Close)
        self.four_hour_trend = self.four_hour_trend_evaluator.evaluate()
        self.Debug(f"Four Hour Trend: {self.four_hour_trend}")

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
        
    def execute_trade(self, order_type, price, setup, time, position_multiplier=1.0):
        # Define position size based on setup type and AI confidence
        base_quantity = 1 if "Setup B" in setup else 1.5
        # For AI Enhanced setups, use the position_multiplier directly
        if "AI Enhanced" in setup:
            quantity = base_quantity * position_multiplier
        else:
            quantity = base_quantity

        if order_type == "buy":
            # Market Order (Instant Execution)
            self.MarketOrder(self.gld, quantity)
            self.Debug(f"{setup} - Market BUY executed at {price} on {time}, Quantity: {quantity}, AI Confidence: {self.ai_confidence:.3f}")

            # Stop Loss & Take Profit Logic
            stop_loss_price = price - self.stop_loss_pips
            take_profit_multiplier = 2 if "Setup B" in setup else 3
            take_profit_price = price + (self.stop_loss_pips * take_profit_multiplier)

            self.StopMarketOrder(self.gld, -quantity, stop_loss_price)  # Stop Loss
            self.LimitOrder(self.gld, quantity, take_profit_price)  # Take Profit

        elif order_type == "sell":
            # Market Order (Instant Execution)
            self.MarketOrder(self.gld, -quantity)
            self.Debug(f"{setup} - Market SELL executed at {price} on {time}, Quantity: {quantity}, AI Confidence: {self.ai_confidence:.3f}")

            # Stop Loss & Take Profit Logic
            stop_loss_price = price + self.stop_loss_pips
            take_profit_multiplier = 2 if "Setup B" in setup else 3
            take_profit_price = price - (self.stop_loss_pips * take_profit_multiplier)

            self.StopMarketOrder(self.gld, quantity, stop_loss_price)  # Stop Loss
            self.LimitOrder(self.gld, -quantity, take_profit_price)  # Take Profit

        self.trade_count += 1

    def reset_trade_count(self):
        self.trade_count = 0
