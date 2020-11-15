from collections import deque
import datetime

import plotly.graph_objects as go
import pandas as pd 

from src.datahandler import fx_datahandler
from src.portfolio import naive_portfolio, sl_tp_portfolio
from src.strategy import linear_regression_strategy
from src.executionhandler import naive_executionhandler

conversions = ["AUD_USD", "EUR_USD", "GBP_USD", "NZD_USD", "USD_CAD",
            "USD_CHF", "USD_CNH", "USD_CZK", "USD_DKK",
            "USD_HKD", "USD_HUF", "USD_JPY", "USD_MXN",
            "USD_NOK", "USD_PLN", "USD_SAR", "USD_SEK",
            "USD_SGD", "USD_THB", "USD_TRY", "USD_ZAR"]

tickers = ["AUD_CAD", "AUD_CHF", "AUD_NZD", "CAD_CHF",
           "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_GBP", "EUR_NZD",
           "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_NZD", "GBP_USD", "NZD_CAD"]

queue = deque()
bars = fx_datahandler.FxDataHandler(queue, conversions+tickers, "D", datetime.datetime(2019, 1, 1), K=100)
#port = naive_portfolio.NaivePortfolio(queue, 1000)
port = sl_tp_portfolio.StopLossTakeProfit(queue, 1000)
strat = linear_regression_strategy.NaiveLinearRegression(queue)
broker = naive_executionhandler.NaiveExecutionHandler(queue)

while True:
    bars.get_latest_data()
    while True:
        if queue:
            if queue[0].get_type() == "MARKET":
                broker.update_conversion(queue[0])
                strat.get_signals(queue[0])
            if queue[0].get_type() == "SIGNAL":
                port.create_order(queue[0])
            if queue[0].get_type() == "ORDER":
                broker.fill_order(queue[0])
            if queue[0].get_type() == "FILL":
                port.update(queue[0])
            queue.popleft()
        else:
            break

    try:
        bars.update()
    except IndexError: # error should be IndexError: pop from empty list
        returns = port.get_history()
        x = [r['return'] for r in returns]
        df = pd.DataFrame({'return': x})
        print(df)
        print('win ratio', len([x for x in x if x > 0]) / len(x))
        print(df.describe())
        fig = go.Figure(data=go.Scatter(y=port.get_equity()))
        fig.show()
        break