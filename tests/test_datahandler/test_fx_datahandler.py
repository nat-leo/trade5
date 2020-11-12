from collections import deque
import datetime

import pytest

from src.datahandler import fx_datahandler
from src import event

def test_datahandler_initialization():
    tickers = ['EUR_USD', 'USD_JPY']
    granularity = 'D'
    queue = deque()
    k = 4
    start_date = datetime.datetime(2020, 11, 2, 0, 0, 0, 0)
    end_date = datetime.datetime(2020, 11, 6, 0, 0, 0, 0)
    fx = fx_datahandler.FxDataHandler(queue, tickers, granularity, start_date, end_date=end_date, K=k)
    assert len(fx.get_data()['EUR_USD']) == 1, f'data size of {len(fx.get_data())} is incorrect'
    assert fx.get_latest_data()['EUR_USD'], f'latest_data not filled on initialization'

def test_get_latest_data():
    tickers = ['EUR_USD', 'USD_JPY']
    granularity = 'M15'
    queue = deque()
    k = 4
    start_date = datetime.datetime(2020, 11, 1, 0, 0, 0, 0)
    end_date = datetime.datetime(2020, 11, 6, 0, 0, 0, 0)
    fx = fx_datahandler.FxDataHandler(queue, tickers, granularity, start_date, end_date=end_date, K=k)
    fx.get_latest_data() 
    assert len(queue) == 2, 'Queue should not be empty'
    assert queue[0].get_ticker() == 'EUR_USD', f'Ticker is not "EUR_USD", but {queue[0].get_ticker}'
    assert queue[1].get_ticker() == 'USD_JPY', f'Ticker is not "USD_JPY", but {queue[1].get_ticker}'
    assert queue[0].get_data()[0]['time'], 'improper formatting for queue[0].get_data[0]["time"]'
    assert queue[0].get_data()[0]['volume'], 'improper formatting for queue[0].get_data[0]["volume"]'
    assert queue[0].get_data()[0]['bid'], 'improper formatting for queue[0].get_data[0]["bid"]'
    assert queue[0].get_data()[0]['ask'], 'improper formatting for queue[0].get_data[0]["ask"]'
    assert len(queue[0].get_data()) == k, f'market data size must be {k}, but is {len(queue[0].get_data())}'

def test_update_data():
    tickers = ['EUR_USD', 'USD_JPY']
    granularity = 'D'
    queue = deque()
    k = 4
    start_date = datetime.datetime(2020, 11, 1, 0, 0, 0, 0)
    end_date = datetime.datetime(2020, 11, 6, 0, 0, 0, 0)
    fx = fx_datahandler.FxDataHandler(queue, tickers, granularity, start_date, end_date=end_date, K=k)
    old_length = len(fx.get_latest_data()['EUR_USD'])
    fx.update()
    assert len(fx.get_latest_data()['EUR_USD']) == old_length+1, f'update should increase length of latest_data by only one'
    fx.update()
    assert not fx.get_data()['EUR_USD'], f'data should be empty, but is {fx.get_data()} after 2 calls to update data with k=4 and old data {old_data}'