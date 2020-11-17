from src import event
from src.strategy import abstract_strategy


class DualMomentum(abstract_strategy.Strategy):
    def __init__(self, events):
        self.events = events

    def get_signals(self, q_event):
        """
        Long the fastest upgrowth, 
        short the fastest downgrowth. 

        example:
        A:+5%, B:+6%, C:-7%, D: +2%,
        Long only A, and Short only C
        """
        pair_performances = {}
        for mkt_event in q_event.get_market_events():
            pair_performances[mkt_event.get_ticker()] = self.calculate_percent_change(mkt_event.get_data()[-1]['bid'][3], 
                                                                                      mkt_event.get_data()[0]['bid'][3])
        ticker = max(pair_performances)
        direction = -1 if pair_performances[max(pair_performances)] < 0 else 1
        for mkt_event in q_event.get_market_events():
            if ticker == mkt_event.get_ticker():
                tick_event = mkt_event
        print(ticker, pair_performances[ticker])
        self.events.append(event.SignalEvent(ticker, direction, tick_event.get_data()[-1]))

    # utility functions
    def calculate_percent_change(self, new_price, old_price):
        return (new_price - old_price) / old_price