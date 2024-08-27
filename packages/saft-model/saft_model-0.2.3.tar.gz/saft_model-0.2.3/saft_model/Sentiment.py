
from enum import Enum

class Sentiment(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

    @classmethod
    def value_of(cls, val: str):
        try: 
            return cls(val.upper())
        except ValueError:
            raise ValueError(f"'{val}' is not a valid {cls.__name__}")