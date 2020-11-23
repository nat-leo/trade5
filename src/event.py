class Event:
    pass


class MarketEvent(Event):
    """
    data or news that comes into the market.
    """
    def __init__(self, ticker, data):
        self.type = 'MARKET'
        self.ticker = ticker
        self.data = data
    
    def __repr__(self):
        return "MarketEvent beginning at" + self.data[0]['time']
    
    def get_type(self):
        return self.type
    
    def get_data(self):
        """ [{'time': date, 'volume': int or float, 'bid': [float, float, float, float], 'ask': [float, float, float, float]}]."""
        return self.data

    def get_ticker(self):
        return self.ticker


class MultipleMarketEvent(Event):
    """
    data or news that comes into the market.
    """
    def __init__(self, market_objects):
        self.type = 'MARKET'
        self.market_objects = market_objects
        for obj in self.market_objects:
            assert isinstance(obj, MarketEvent)

    def __repr__(self):
        return "MarketEvent beginning at" + self.market_objects[0].get_data()[0]['time']
    
    def get_type(self):
        return self.type
    
    def get_market_events(self):
        return self.market_objects
    

class SignalEvent(Event):
    """
    Strategy objects send signals to Portfolio objects.
    SignalEvent handles the signal

    parameters:
    direction - '-1' or '1'
    """
    def __init__(self, ticker, direction, candle):
        self.type = 'SIGNAL'
        self.ticker = ticker
        self.direction = direction
        self.candle = candle
    
    def get_type(self):
        return self.type
    
    def get_ticker(self):
        return self.ticker
    
    def get_direction(self):
        return self.direction
    
    def get_candle(self):
        return self.candle


class OrderEvent(Event):
    """
    When Portfolio objects receive a new SignalEvent object, they respond 
    by creating an OrderEvent object that includes information like the time
    the order was created, the ticker symbol for the order, the order size,
    
    parameters:
    direction - 'BUY' or 'SELL'.
    ticker - ticker symbol of security.
    datetime - datetime the event was created.
    quantity - nonnegative integer of the amount of units to buy/sell.
    """
    def __init__(self, direction, datetime, ticker, quantity, price=None, stop_loss=None, take_profit=None):
        self.type = 'ORDER'
        self.ticker = ticker
        self.quantity = quantity
        self.direction = direction
        self.datetime = datetime
        self.price = price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def get_type(self):
        return self.type
    
    def get_ticker(self):
        return self.ticker
    
    def get_quantity(self):
        return self.quantity
    
    def get_direction(self):
        return self.direction
    
    def get_datetime(self):
        return self.datetime
    
    def get_price(self):
        return self.price

    def get_stop_loss(self):
        return self.stop_loss

    def get_take_profit(self):
        return self.take_profit


class FillEvent(Event):
    """
    FillEvent objects are responses to order objects

    Parameters:
    ticker - ticker symbol of security.
    datetime - time the order was filled.
    quantity - amount of units filled.
    price - price at which the units were filled.
    commission - cost of getting a fill.
    """
    def __init__(self, direction, ticker, quantity, price, pip_val, margin, candle=None):
        self.type = 'FILL'
        self.ticker = ticker
        self.quantity = int(quantity)
        self.price = float(price)
        self.direction = direction
        self.pip_val = pip_val
        self.margin = margin
        self.candle = candle
    
    def get_type(self):
        return self.type
    
    def get_ticker(self):
        return self.ticker
    
    def get_quantity(self):
        return self.quantity

    def get_price(self):
        return self.price
    
    def get_direction(self):
        return self.direction
    
    def get_pip_val(self):
        return self.pip_val
    
    def get_margin(self):
        return self.margin
    
    def get_candle(self):
        return self.candle
    
