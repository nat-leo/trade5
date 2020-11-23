from collections import deque

import pytest

from src.portfolio import single_hold_portfolio
from src import event


def test_create_order():
    """
    create_order must create an order for the ticker
    create_order must then close any other holding
    if signal is for a ticker already held, disregard new signal 
    """
    port = single_hold_portfolio.SingleHoldPortfolio(deque(), 1000)

    signal = event.SignalEvent('USD_JPY', 1, {'time': 'arbitrary_time', 
                                               'volume': 12345, 
                                               'bid': [float, 1.8400, 1.6000, float], 
                                               'ask': [float, 1.8420, 1.6020, float]})
    port.create_order(signal)
    with pytest.raises(KeyError):
        port.get_holding('USD_JPY')
    e = port.get_events()
    assert len(e) == 1, 'there should be two orders if holding ticker != signal ticker'
    assert e[0].get_quantity() == 40000, 'closing quantity must equal holding quantity'
    assert e[0].get_ticker() == 'USD_JPY', 'make the new holding last to get filled.'