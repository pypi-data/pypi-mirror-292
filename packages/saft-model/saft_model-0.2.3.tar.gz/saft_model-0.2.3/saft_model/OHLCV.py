
from saft_model.TimeInterval import TimeInterval

class OHLCV():
    def __init__(self, ticker: str, measured_at: int, time_interval: TimeInterval, open: int, high: int, low: int, close: int, volume: int) -> None:
        self.ticker = ticker
        self.measured_at = measured_at # millis since epoch
        self.time_interval = time_interval

        # all monetary values in cents
        self.open = open
        self.high = high 
        self.low = low 
        self.close = close

        self.volume = volume