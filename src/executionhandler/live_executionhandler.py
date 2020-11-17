import json

from decouple import config
import requests

from src.executionhandler import naive_executionhandler
from src import event

ACCOUNT = config('ACCOUNT_NUMBER')
LIVE_ACCOUNT = config('LIVE_ACCOUNT_NUMBER')
PRACTICE_TOKEN = config('PRACTICE_TRADE_TOKEN')
LIVE_TOKEN = config('LIVE_TRADE_TOKEN')
PRACTICE_HEADER = {
    'Content-Type': 'application/json',
    'Authorization': PRACTICE_TOKEN, # change this to live when in production
}
LIVE_HEADER = {
    'Content-Type': 'application/json',
    'Authorization': LIVE_TOKEN, # change this to live when in production
}


class Live(naive_executionhandler.NaiveExecutionHandler):
    def fill_order(self, q_event):
        self.order(q_event.get_direction(), q_event.get_ticker(), q_event.get_quantity())
        price = q_event.get_datetime()['bid'][3] if q_event.get_direction() < 0 else q_event.get_datetime()['ask'][3]
        self.events.append(event.FillEvent(
            direction=q_event.get_direction(), 
            ticker=q_event.get_ticker(), 
            quantity=q_event.get_quantity(),
            price=price,
            pip_val=self.set_pip_value(q_event.get_ticker(), price, q_event.get_quantity()),
            margin=self.convert_to_usd(q_event.get_ticker(), q_event.get_quantity())
        ))
        print(f'execution filled order for {q_event.get_ticker()}')

    def order(self, direction, ticker, quantity):
        """ executes a short order using Oanda API

        Args:
            currency_pair: a string, must be all caps like "EUR_USD". convert a currency pair you'd see
            like EUR/USD or USD/JPY to EUR_USD or USD_JPY respectively.
            order_size: an integer, the number of units of the currency pair to be ordered
        
        Returns:
            An integer representing the HTTP status code of the API call
        """
        params = {
            "order": {
                "units": str(direction*quantity),
                "instrument": ticker,
                "timeInForce": "IOC",
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }
        response = requests.post(f"https://api-fxpractice.oanda.com/v3/accounts/{ACCOUNT}/orders", 
                                headers=PRACTICE_HEADER, data=json.dumps(params))
        print('order in ', response.status_code, direction*quantity)
        return response.status_code
