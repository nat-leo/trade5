from src import event
from src.executionhandler import abstract_executionhandler

class NaiveExecutionHandler(abstract_executionhandler.ExecutionHandler):
    """
    always fills orders. Does not account for slippage.
    """
    def __init__(self, events):
        self.events = events
        self.conversions = {
            "AUD_USD": float,
            "EUR_USD": float,
            "GBP_USD": float,
            "NZD_USD": float,
            "USD_CAD": float,
            "USD_CHF": float,
            "USD_CNH": float,
            "USD_CZK": float,
            "USD_DKK": float,
            "USD_HKD": float,
            "USD_HUF": float,
            "USD_JPY": float,
            "USD_MXN": float,
            "USD_NOK": float,
            "USD_PLN": float,
            "USD_SAR": float,
            "USD_SEK": float,
            "USD_SGD": float,
            "USD_THB": float,
            "USD_TRY": float,
            "USD_ZAR": float,
        }

    def fill_order(self, q_event):
        self.events.append(event.FillEvent(
            direction=q_event.get_direction(), 
            ticker=q_event.get_ticker(), 
            quantity=q_event.get_quantity(),
            price=q_event.get_datetime()['bid'][3] if q_event.get_direction() < 0 else q_event.get_datetime()['ask'][3],
            pip_val=self.calculate_pip_val(q_event)
        ))
    
    def update_conversion(self, q_event):
        """updates conversion table with a MarketEvent."""
        ticker = q_event.get_ticker()
        new_conversion = q_event.get_data()[-1]
        if ticker in self.conversions:
            self.conversions[ticker] = new_conversion
        #print('conversion table:', self.conversions)
    
    def calculate_pip_val(self, q_event):
        """ uses OrderEvent and conversion table to calculate USD per pip."""
        if q_event.get_direction() < 0:
            b_a = 'bid'
        else:
            b_a = 'ask'
        base_currency_pips =  q_event.get_quantity() * (0.0001/q_event.get_datetime()[b_a][3])
        base = q_event.get_ticker()[:3]
        conversion = 0
        for ticker in self.conversions:
            if ticker.startswith(base):
                pip_val = base_currency_pips * self.conversions[ticker][b_a][3]
            elif ticker.endswith(base):
                pip_val = base_currency_pips / self.conversions[ticker][b_a][3]
            else:
                print('ticker not found for', ticker)
        return pip_val