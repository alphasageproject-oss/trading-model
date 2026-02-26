# Technical Indicators

# This module contains various technical indicator models that can be used for trading strategies.

class MovingAverage:
    def __init__(self, period):
        self.period = period
        self.values = []

    def add_value(self, value):
        self.values.append(value)
        if len(self.values) > self.period:
            self.values.pop(0)

    def calculate(self):
        if len(self.values) < self.period:
            return None
        return sum(self.values) / self.period

class RSI:
    def __init__(self, period):
        self.period = period
        self.gains = []
        self.losses = []

    def add_value(self, value):
        # Add logic to calculate RSI values
        pass

    def calculate(self):
        # Add logic to compute RSI
        pass

class MACD:
    def __init__(self, short_period, long_period, signal_period):
        self.short_period = short_period
        self.long_period = long_period
        self.signal_period = signal_period

    def add_value(self, value):
        # Add logic to calculate MACD values
        pass

    def calculate(self):
        # Add logic to compute MACD
        pass
