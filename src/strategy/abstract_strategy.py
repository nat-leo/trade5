from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def get_signals(self, event):
        """
        adds a signal event to the queue
        """
        pass