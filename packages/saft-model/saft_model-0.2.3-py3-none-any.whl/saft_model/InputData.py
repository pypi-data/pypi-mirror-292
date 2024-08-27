
from typing import List

from saft_model.TimeInterval import TimeInterval
from saft_model.OHLCV import OHLCV

class InitialData():
    def __init__(self, name: str, ticker: str, time_interval: TimeInterval, measurements: List[OHLCV]) -> None:
        self.name = name # unique identifier
        self.ticker = ticker
        self.time_interval = time_interval
        self.measurements = measurements

class ReoccurData():
    def __init__(self, ticker: str, time_interval: TimeInterval, measurements: List[OHLCV]) -> None:
        self.ticker = ticker
        self.time_interval = time_interval
        self.measurements = measurements

class InputData():
    def __init__(self, initial_data_lst: List[InitialData], reoccur_data_list: List[ReoccurData]) -> None:
        self.initial_data: List[InitialData] = initial_data_lst
        self.reoccur_data: List[ReoccurData] = reoccur_data_list

    