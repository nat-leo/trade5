from abc import ABC, abstractmethod


class ExecutionHandler(ABC):
    """
    executes orders, creates FillEvents that are used to update portfolio objects. 
    """
    @abstractmethod
    def fill_order(self):
        pass