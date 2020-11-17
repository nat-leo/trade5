from collections import deque

import pytest

from src.strategy import dual_momentum_strategy
from src import event

def test_dual_momentum_signal():
    queue = deque()
    strat = dual_momentum_strategy.DualMomentum(queue)
    pair1 = event.MarketEvent('EUR_USD', [{'time': 'yada', 'volume': int or float, 'bid': [float, float, float, 10], 'ask': [float, float, float, 11]},
                                          {'time': 'yada2', 'volume': int or float, 'bid': [float, float, float, 12], 'ask': [float, float, float, 13]}])
    pair2 = event.MarketEvent('USD_JPY', [{'time': 'yada', 'volume': int or float, 'bid': [float, float, float, 10], 'ask': [float, float, float, 11]},
                                          {'time': 'yada2', 'volume': int or float, 'bid': [float, float, float, 13], 'ask': [float, float, float, 14]}])
    data = event.MultipleMarketEvent([pair1, pair2])

    strat.get_signals(data)
    assert isinstance(queue[-1], event.SignalEvent)
    assert queue[-1].get_ticker() == 'USD_JPY'
    assert queue[-1].get_direction() == 1
