from collections import deque
import datetime

import pytest

from src.executionhandler import naive_executionhandler
from src import event


@pytest.fixture
def broker():
    queue = deque()
    broker = naive_executionhandler.NaiveExecutionHandler(queue)
    return broker

def test_calculate_pip_value(broker):
    assert 0.089 < broker.calculate_pip_val('USD_JPY', 105.111, 1000) < 0.096, f'calculation does not equal pip value'
    assert 0.1312 < broker.calculate_pip_val('AUD_JPY', 76.000, 1000) < 0.1316, f'calculation does not equal pip value'
    assert 0.083 < broker.calculate_pip_val('EUR_USD', 1.18068, 1000) < 0.085, f'calculation does not equal pip value'
    assert 0.024 < broker.calculate_pip_val('USD_MXN', 20.63630, 5000) < 0.025, f'calculation does not equal pip value'
    assert 0.10 < broker.calculate_pip_val('USD_CHF', 0.91521, 1000) < 0.11, f'calculation does not equal pip value'

def test_convert_to_usd(broker):
    broker.set_conversion("EUR_USD", 1.18060)
    assert 1180.59 < broker.convert_to_usd("EUR_USD", 1000) < 1180.61, f'calculation does not equal conversion'
    assert 1180.59 < broker.convert_to_usd("EUR_TRY", 1000) < 1180.61, f'calculation does not equal conversion'
    broker.set_conversion("EUR_USD", 1.18068)
    assert 0.099 < broker.convert_to_usd("EUR_USD", 0.0846) < 0.11, f'calculation does not equal conversion'
    broker.set_conversion("EUR_USD", 1.18034)
    assert 1180.33 < broker.convert_to_usd("EUR_SEK", 1000) < 1180.35, f'calculation does not equal conversion'
    broker.set_conversion("USD_SEK", 8.64145)
    assert 999.99 < broker.convert_to_usd("USD_SEK", 1000) < 1000.01, f'calculation does not equal conversion'
    
