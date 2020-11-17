from src.portfolio import naive_portfolio
from src import event

class StopLossTakeProfit(naive_portfolio.NaivePortfolio):
    """" Naive Portfolio with a Stop Loss and Take Profit."""
    def __init__(self, events, equity):
        self.events = events
        self.holdings = {}
        self.history = []
        self.equity = [equity]
    
    def create_order(self, q_event):
        """
        Append an OrderEvent to the queue (typically after receiving a SignalEvent 
        from a strategy object, or after a MarketEvent hits a stoploss or takeprofit). 
        """
        self.events.append(event.OrderEvent(
            direction=q_event.get_direction(), 
            datetime= q_event.get_datetime(),
            ticker=q_event.get_ticker(), 
            quantity=40000
        ))
        print('portfolio created an order')
    
    def create_close_order(self, ticker, direction, datetime, price, quantity=40000):
        """For takeprofit / stoploss caused OrderEvents. """
        self.events.append(event.OrderEvent(
            direction=direction, 
            datetime=datetime,
            ticker=ticker,
            price=price,
            quantity=quantity
        ))

    def update(self, q_event):
        """
        After receiving a FillEvent, update internal data to the FillEvent's 
        specifications.
        """
        if q_event.get_ticker() in self.holdings: # if an open order needs to be closed
            holding = self.holdings[q_event.get_ticker()]
            self.history.append({
                'ticker': holding['ticker'],
                'direction': holding['direction'],
                'price': holding['price'],
                'return': self.calculate_return(holding['ticker'], holding['direction'], holding['price'], q_event.get_price(), holding['pip_value']),
                'pip_value': holding['pip_value']
            })
            self.equity.append(self.equity[-1] + self.calculate_return(holding['ticker'], holding['direction'], holding['price'], q_event.get_price(), holding['pip_value']))
            del self.holdings[q_event.get_ticker()]
            print('portfolio added a trade entry')
        else: # add order to holdings
            self.holdings[q_event.get_ticker()] = {
                'ticker': q_event.get_ticker(),
                'direction': q_event.get_direction(),
                'quantity': q_event.get_quantity(),
                'price': q_event.get_price(),
                'pip_value': q_event.get_pip_val(),
                'margin': q_event.get_margin(),
                'stop_loss': self.set_stop_loss(q_event.get_ticker(), q_event.get_direction(), q_event.get_price(), 200),
                'take_profit': self.set_take_profit(q_event.get_ticker(), q_event.get_direction(), q_event.get_price(), 500)
            }
            print('portfolio updated holdings')

    def check_if_close_triggered(self, q_event):
        """Takes a MarketEvent and checks if the candle would have triggered one of the 
        holdings to close. """
        tick = q_event.get_ticker()
        _dir = self.holdings[tick]['direction']
        date = q_event.get_data()[-1]['time']
        bid = q_event.get_data()[-1]['bid']
        ask = q_event.get_data()[-1]['ask']

        if _dir < 0: # if short (buy bid)
            if bid[1] > self.holdings[tick]['stop_loss']:
                # create an OrderEvent, pop holding out of holdings and into history
                self.create_close_order(tick, _dir, date, self.holdings[tick]['stop_loss'])
            elif bid[2] < self.holdings[tick]['take_profit']:
                # create an OrderEvent, pop holding out of holdings and into history
                self.create_close_order(tick, _dir, date, self.holdings[tick]['take_profit'])
        elif _dir > 0: # if long (sell ask)
            if ask[2] < self.holdings[tick]['stop_loss']:
                self.create_close_order(tick, _dir, date, self.holdings[tick]['stop_loss'])
            elif ask[1] < self.holdings[tick]['take_profit']:
                self.create_close_order(tick, _dir, date, self.holdings[tick]['take_profit'])

    # utility functions
    def set_stop_loss(self, ticker, direction, price, pips):
        if ticker.startswith('JPY') or ticker.endswith('JPY'):
            if direction > 0:
                sl = 0.01*pips - price
            elif direction < 0:
                sl = 0.01*pips + price
        else:
            if direction > 0:
                sl = 0.0001*pips - price
            elif direction < 0:
                sl = 0.0001*pips + price
        return sl
                
    def set_take_profit(self, ticker, direction, price, pips):
        if ticker.startswith('JPY') or ticker.endswith('JPY'):
            if direction > 0:
                tp = 0.01*pips + price
            elif direction < 0:
                tp = 0.01*pips - price
        else:
            if direction > 0:
                tp = 0.0001*pips + price
            elif direction < 0:
                tp = 0.0001*pips - price
        return tp
    
    def calculate_return(self, ticker, direction, price, new_price, pip_value):
        if ticker.startswith('JPY') or ticker.endswith('JPY'):
            rate = 0.01
        else:
            rate = 0.0001
        if direction > 0: # if we selling a long
            return (new_price - price) / rate * pip_value
        elif direction < 0: # if we covering a short
            return (price - new_price) / rate * pip_value

    #getters and setters
    def get_all_holdings(self):
        return self.holdings
    
    def get_events(self):
        return self.events

    def get_equity(self):
        return self.equity
    
    def get_history(self):
        return self.history

    def get_holding(self, ticker):
        return self.holdings[ticker]
    
    def set_holding(self, ticker, direction, quantity, price, stop_loss, take_profit):
        self.holdings[ticker] = {
            'ticker': ticker,
            'direction': direction,
            'quantity': quantity,
            'price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
