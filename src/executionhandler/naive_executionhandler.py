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
            pip_val=None
        ))
    
    def update_conversion(self, q_event):
        """updates conversion table with a MarketEvent."""
        pass
    
    def calculate_pip_val(self, ticker, rate, value):
        """ Calculate pip value from any amount.

        use the formula:

        pip_val of currency = units of currency * 0.0001 / price of pair
                                                  0.01 / price of pair for /JPY pairs

        Example:
        ABC/CDE = 1.5
        ABC is the base currency, and CDE is the quoted currency.

        if you buy 100 units of ABC/CDE, you get a pip value:
        pip_val = 100 * 0.00001/1.5 = 0.00666 ABC per pip
        """
        if ticker.startswith('JPY') or ticker.endswith('JPY'):
            return value * 0.01/rate
        else:
            return value * 0.0001/rate
    
    def convert_to_usd(self, ticker, value):
        """Take any non-USD amount and convert it to USD, can be any either 
        the foreign currency, or the foreign currency per pip (where the pip value 
        already accounts for the order size).
        
        Example: 
        ABC/CDE = 1.5
        ABC/LHF = 0.75
        ABC is the base currency, CDE is the quoted currency, 
        When you buy 100 units of ABC/CDE, you get a trade value of 100 ABC.
        If your account currency is LHF, you convert 100 ABC -> LHF to get your
        trade value in LHF.

        ABC * (LHF/ABC) = LHF
        ABC/LHF = 0.75 -> LHF/ABC = 1 / 0.75
        100 ABC * 1/0.75 LHF/ABC = 133.33333 LHF

        LHF * (ABC/LHF) = ABC
        100LHF * 0.75 ABC/LHF =  75 ABC
        """
        if ticker[:3] == 'USD':
            return value
        try:
            rate = self.conversions[ticker[:3]+'_USD']
            return value * rate
        except KeyError:
            rate = self.conversions['USD_'+ticker[:3]]
            return value * 1/rate 

    # getters and setters
    def get_events(self):
        return self.events

    def get_all_conversions(self):
        return self.conversions
    
    def get_conversion(self, ticker):
        if ticker in self.conversions:
            return self.conversions[ticker]
        else:
            return 'Conversion rate not found.'
    
    def set_conversion(self, pair, rate):
        assert pair in self.conversions, f'pair {pair} not found in conversions'
        self.conversions[pair] = rate
