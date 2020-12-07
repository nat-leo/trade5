from src import event
from src.strategy import abstract_strategy


class DualMomentum(abstract_strategy.Strategy):
    def __init__(self, events):
        self.events = events
        self.timer = 0

    def get_signals(self, q_event):
        """
        Long the fastest upgrowth, 
        short the fastest downgrowth. 

        example:
        A:+5%, B:+6%, C:-7%, D:+2%,
        Long only A, and Short only C
        """
        pair_performances = {}
        for mkt_event in q_event.get_market_events():
            pair_performances[mkt_event.get_ticker()] = self.calculate_percent_change(mkt_event.get_data()[-1]['bid'][3], 
                                                                                    mkt_event.get_data()[0]['bid'][3])
        sorted_performances = [{'ticker': k, 'performance': v} for k, v in sorted(pair_performances.items(), key=lambda item: item[1])]
        
        for performance in sorted_performances[-3:]:
            for mkt_event in q_event.get_market_events():
                if mkt_event.get_ticker() == performance['ticker']:
                    data = mkt_event.get_data()[-1]
            self.events.append(event.SignalEvent(performance['ticker'], 1, data))
        return pair_performances

    # utility functions
    def calculate_percent_change(self, new_price, old_price):
        return (new_price - old_price) / old_price
