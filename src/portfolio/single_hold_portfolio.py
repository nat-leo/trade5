from src.portfolio import naive_portfolio
from src import event

class SingleHoldPortfolio(naive_portfolio.NaivePortfolio):
    """" Naive Portfolio with a Stop Loss and Take Profit."""
    def __init__(self, events, equity):
        self.events = events
        self.holdings = {}
        self.history = []
        self.equity = [equity]
    
    def create_order(self, q_event):
        """
        Get a SignalEvent and enter accordingly, but also get rid of the 
        other holdigns.
        """
        if q_event.get_ticker() not in self.holdings:
            #create order to get rid of old holdings
            if self.holdings:
                for h in self.holdings:
                    print('holding', h)
                    self.events.append(event.OrderEvent(
                        direction=1 if self.holdings[h]['direction']<0 else -1, 
                        datetime=self.holdings[h]['candle'],
                        ticker=self.holdings[h]['ticker'], 
                        quantity=self.holdings[h]['quantity']
                    ))
            # create order for new holding
            self.events.append(event.OrderEvent(
                direction=q_event.get_direction(), 
                datetime= q_event.get_candle(),
                ticker=q_event.get_ticker(), 
                quantity=40000
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
            #print('portfolio added a trade entry')
        else: # add order to holdings
            self.holdings[q_event.get_ticker()] = {
                'ticker': q_event.get_ticker(),
                'direction': q_event.get_direction(),
                'quantity': q_event.get_quantity(),
                'price': q_event.get_price(),
                'pip_value': q_event.get_pip_val(),
                'margin': q_event.get_margin(),
                'candle': q_event.get_candle()
            }
            #print('portfolio updated holdings')

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
