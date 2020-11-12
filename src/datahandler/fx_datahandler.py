""" Forex Datahandler sub-Class.

Contains all Datahandler required methods, and uses 
the Oanda API to fill a dictionary of data. At each tick,
data gets moved from data into another dictionary, where the 
last K points are used to creaste MarketEvent objects.
"""

from collections import deque
import datetime
import json

from decouple import config
import requests

from src import event
from src.datahandler import abstract_datahandler

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


class FxDataHandler(abstract_datahandler.DataHandler):
    """ DataHandler Object for the Spot Foreign Exchange Market.

    parameters:
    queue: a queue data structure
    data: dictionary of all data points needed in the form {currency: [data_points]}
    """
    def __init__(self, queue, tickers, granularity, start_date, end_date=datetime.datetime.utcnow(), K=1):
        self.queue = queue
        self.tickers = tickers
        self.granularity = granularity
        self.start_date = start_date
        self.end_date = end_date
        self.K = K
        self.data = {}
        self.latest_data = {}

        # initialize data with api called data points, then pop first K points to latest data
        for ticker in self.tickers:
            self.data[ticker] = deque(self._get_candles(ticker))
            popped_points = []
            for i in range(self.K):
                popped_points.append(self.data[ticker].popleft()) 
            self.latest_data[ticker] = popped_points

    def update(self):
        """ Remove the next earliest point from data and append it to latest_data. """
        if self.data:
            for ticker in self.tickers:
                if self.data[ticker]:
                    self.latest_data[ticker].append(self.data[ticker].popleft())

    # utility functions
    def _get_candles(self, ticker):
        """ api call to fill self.data with data points for each ticker. """
        data = (
            ('price', 'BA'),
            ('from', self.start_date.isoformat("T") + "Z"),
            ('to', self.end_date.isoformat("T") + "Z"),
            ('granularity', str(self.granularity))
        )

        response = requests.get(f"https://api-fxtrade.oanda.com/v3/instruments/{ticker}/candles", 
                                        headers=LIVE_HEADER, params=data)
        parsed_response = json.loads(response.text)
        #print(parsed_response)
        if response.status_code != 200: # throw error if GET doesn't go through
            raise Exception(ValueError, f"status code is not 200, but {response.status_code} at {ticker}")
        candles = []
        for i in range(len(parsed_response['candles'])): # iterate through the number of candles we got.
            next_candle = {'time': parsed_response['candles'][i]['time'],
                           'volume': float(parsed_response['candles'][i]['volume']),
                           'bid': [float(parsed_response['candles'][i]['bid']['o']), 
                                float(parsed_response['candles'][i]['bid']['h']),
                                float(parsed_response['candles'][i]['bid']['l']),
                                float(parsed_response['candles'][i]['bid']['c'])],
                           'ask': [float(parsed_response['candles'][i]['ask']['o']), 
                                float(parsed_response['candles'][i]['ask']['h']),
                                float(parsed_response['candles'][i]['ask']['l']),
                                float(parsed_response['candles'][i]['ask']['c'])],}
            candles += [next_candle]
        #df = pd.DataFrame(candles)
        return candles

    # getters and setters
    def get_latest_data(self):
        """ Create a MarketEvent Object and place in the queue. """
        for ticker in self.tickers:
            market_data = self.latest_data[ticker][-self.K:]
            self.queue.append(event.MarketEvent(ticker, market_data))
        return self.latest_data

    def get_data(self):
        return self.data

    def get_tickers(self):
        return self.tickers