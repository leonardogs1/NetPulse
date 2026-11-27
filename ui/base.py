from abc import ABC, abstractmethod


class BaseWindow(ABC):
    """Baseline live table of integrated utilities"""

    def __init__(self):
        pass
    
    @abstractmethod
    def  _set_cell(self, row, col, text):
        pass
