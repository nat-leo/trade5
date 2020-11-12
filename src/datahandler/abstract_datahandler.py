"""abstract class for datahandler-type objects. """

from abc import ABC, abstractmethod


class DataHandler(ABC):
    @abstractmethod
    def get_latest_data(self):
        """
        returns the latest N bars of ticker symbol
        """
        raise NotImplementedError("class did not implement get_latest_bars()")

    @abstractmethod
    def update(self):
        """
        returns the latest N bars of ticker symbol
        """
        raise NotImplementedError("class did not implement update_data()")