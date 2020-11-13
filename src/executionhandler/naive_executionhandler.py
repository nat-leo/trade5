from src import event
from src.executionhandler import abstract_executionhandler

class NaiveExecutionHandler(abstract_executionhandler.ExecutionHandler):
    """
    always fills orders. Does not account for slippage.
    """
    def __init__(self, events):
        self.events = events
        self.conversions = {
            "AUD_USD": {},
            "EUR_USD": {},
            "GBP_USD": {},
            "NZD_USD": {},
            "USD_CAD": {},
            "USD_CHF": {},
            "USD_CNH": {},
            "USD_CZK": {},
            "USD_DKK": {},
            "USD_HKD": {},
            "USD_HUF": {},
            "USD_JPY": {},
            "USD_MXN": {},
            "USD_NOK": {},
            "USD_PLN": {},
            "USD_SAR": {},
            "USD_SEK": {},
            "USD_SGD": {},
            "USD_THB": {},
            "USD_ZAR": {},
            "USD_TRY": {},
        }

    def fill_order(self, q_event):
        price = q_event.get_datetime()['bid'][3] if q_event.get_direction() < 0 else q_event.get_datetime()['ask'][3]
        self.events.append(event.FillEvent(
            direction=q_event.get_direction(), 
            ticker=q_event.get_ticker(), 
            quantity=q_event.get_quantity(),
            price=price,
            pip_val=self.set_pip_value(q_event.get_ticker(), price, q_event.get_quantity())
        ))
    
    def update_conversion(self, q_event):
        """updates conversion table with a MarketEvent."""
        if q_event.get_ticker() in self.conversions:
            midpoint = (q_event.get_data()[-1]['bid'][3] + q_event.get_data()[-1]['ask'][3]) / 2
            self.conversions[q_event.get_ticker()] = midpoint

    def set_pip_value(self, ticker, rate, value):
        """called on an OrderEvent"""
        pip_val = self.calculate_pip_val(ticker, rate, value)
        pip_val_in_usd = self.convert_to_usd(ticker, pip_val)
        return pip_val_in_usd

    # helpers
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
