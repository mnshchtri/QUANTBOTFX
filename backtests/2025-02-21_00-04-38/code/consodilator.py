# region imports
# from AlgorithmImports import *
# from datetime import timedelta
"""class Create_Consolidators():
    def  __init__(self,algorithm,gld):
        self.algorithm = algorithm
        self.gld =gld

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

         # Create the 5-minute consolidator
        self.five_minute_consodilator = TradeBarConsolidator(timedelta(minutes=5))
        self.SubscriptionManager.AddConsolidator(self.gld, self.five_minute_consodilator)
        self.five_minute_consodilator.DataConsolidated += self.on_five_min_data

# Your New Python File """
