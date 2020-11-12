import src.event
from src.portfolio import portfolio


class NaivePortfolio(portfolio.Portfolio):
    """
    just buys and sells 1000 units of the ticker, with no 
    order sizing, or risk management.
    """
    def __init__(self, events, equity):
        self.events = events
        self.holdings = {}
        self.history = []
        self.equity = [equity]

    def create_order(self, q_event):
        self.events.append(event.OrderEvent(
            direction=q_event.get_direction(), 
            datetime= q_event.get_datetime(),
            ticker=q_event.get_ticker(), 
            quantity=1000
        ))

    def update(self, q_event):
        ticker = q_event.get_ticker()
        new_direction = q_event.get_direction()
        new_quantity = q_event.get_quantity()
        new_price = q_event.get_price()
        print('pip val:', q_event.get_pip_val(), ticker)
        if ticker in self.holdings:
            old_price = self.holdings[ticker]['price']
            old_direction = self.holdings[ticker]['direction']
            if self._is_long(ticker):
                trade_return = new_price - old_price
            else:
                trade_return = old_price - new_price
            if new_direction != old_direction:
                self.history.append({
                    'ticker': ticker, 
                    'return': trade_return
                })
                self.holdings.pop(ticker)
        else:
            self.holdings[ticker] = {
                'ticker': ticker,
                'direction': new_direction,
                'quantity': new_quantity,
                'price': new_price
            }

    def get_returns(self):
        return self.history
    
    # helpers
    def _is_long(self, ticker):
        if self.holdings[ticker]['direction'] < 0: # if short
            return False
        else:
            return True