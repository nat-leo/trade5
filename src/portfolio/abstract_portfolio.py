from abc import ABC, abstractmethod


class Portfolio(ABC):
    """
    Portfolios contain all the tickers that can be bought,
    a history of returns, and a list of current holdings.
    """
    @abstractmethod
    def create_order(self):
        """
        create event for execution handler.
        needs: ticker, quantity, stoploss, takeprofit
        """
        pass

    @abstractmethod
    def update(self):
        """
        use FillEvent (sent from ExecutionHandler object) to update holdings 
        (self.holding) by deleting now closed positions and recording results 
        in history, and updating the portfolio with orders (OrderEvents go to 
        an ExecutionHandler object) that were successfully filled.
        parameters:
        q_event - a FillEvent object (event.py)
        """
        pass