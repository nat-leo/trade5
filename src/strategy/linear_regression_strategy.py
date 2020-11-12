from sklearn import linear_model
from hurst import compute_Hc

import numpy as np
import pandas as pd

from src import event
from src.strategy import abstract_strategy

class NaiveLinearRegression(abstract_strategy.Strategy):
    def __init__(self, queue):
        self.queue = queue

    def get_signals(self, q_event):
        data = q_event.get_data()
        model = linear_model.LinearRegression()
        X = np.array([i for i in range(1, len(data)+1)]).reshape(-1, 1)
        y = np.array([d['bid'][3] for d in data]).reshape(-1, 1)
        #h_e = compute_Hc(y, kind='price', simplified=True)
        model.fit(X, y)
        if model.coef_ < 0:
            self.queue.append(event.SignalEvent(q_event.get_ticker(), -1, data[-1]))
            return -1
        elif model.coef_ > 0:
            self.queue.append(event.SignalEvent(q_event.get_ticker(), 1, data[-1]))
            return 1
        else: 
            return 0