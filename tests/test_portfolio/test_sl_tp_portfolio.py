from collections import deque

import pytest 

from src.portfolio import sl_tp_portfolio
from src import event


@pytest.fixture
def portfolio():
    port = sl_tp_portfolio.StopLossTakeProfit(deque(), 1000)
    port.set_holding('EUR_USD', direction=1, quantity=1000, 
                     price=1.5000, stop_loss=1.3000, take_profit=1.7000)
    return port

def test_trigger_fill(portfolio):
    trigger_sl = event.MarketEvent('EUR_USD', [{'time': str, 
                                               'volume': int, 
                                               'bid': [float, 1.4000, 1.2500, float], # buy ask, sell bid
                                               'ask': [float, 1.4020, 1.2520, float]}])
    trigger_tp = event.MarketEvent('EUR_USD', [{'time': 'arbitrary_time', 
                                               'volume': 12345, 
                                               'bid': [float, 1.8400, 1.6000, float], 
                                               'ask': [float, 1.8420, 1.6020, float]}])
    no_trigger = event.MarketEvent('EUR_USD', [{'time': str, 
                                               'volume': int, 
                                               'bid': [float, 1.4999, 1.3001, float], 
                                               'ask': [float, 1.5019, 1.3021, float]}])
    portfolio.check_if_close_triggered(trigger_sl)
    portfolio.check_if_close_triggered(trigger_tp)
    portfolio.check_if_close_triggered(no_trigger)
    assert len(portfolio.get_events()) == 2, f'there chould be 2 ORDER events in queue, not {len(portfolio.get_events())}'
    for e in portfolio.get_events():
        assert e.get_ticker() == 'EUR_USD', f'ticker {e.get_ticker()} not in events'
        assert e.get_type() == 'ORDER', f'event type of {e.get_type()} not an ORDER'

def test_update():
    portfolio = sl_tp_portfolio.StopLossTakeProfit(deque(), 1000)
    init = event.FillEvent(1, 'EUR_USD', 1000, 1.5000, 0.1, 1300)
    portfolio.update(init)
    trigger_tp = event.FillEvent(-1, 'EUR_USD', 1000, 1.8000, 0.1, 1300)
    portfolio.update(trigger_tp)
    with pytest.raises(KeyError):
        portfolio.get_holding('EUR_USD')
    assert 2.99999 < portfolio.get_history()[-1]['return'] < 300.00001
    assert portfolio.get_history()[-1]['ticker'] == 'EUR_USD'
    assert portfolio.get_history()[-1]['pip_value'] == 0.1