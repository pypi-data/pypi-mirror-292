
from typing import List
import datetime as dt
from datetime import datetime
from enum import Enum

from saft_model.TimeInterval import TimeInterval

class TimeAnchor(Enum):
    """
    Describes a specific point in time relative to the current runtime's date
    """
    intendedModelStartTime = "intendedModelStartTime"
    marketOpenToday = "marketOpenToday"


class InitialDataRequirement():
    """
    A data requirement that is gathered immediately on beginning of Tribe Member runtime 
    """
    def __init__(self, 
                 id: str,
                 name: str, 
                 ticker: str, 
                 time_anchor: TimeAnchor,
                 offset_start_ms: int,
                 interval_to_measure_at: TimeInterval, 
                 offset_end_ms: int = None) -> None:
        self.id = id
        self.name = name
        self.ticker = ticker
        self.time_anchor = time_anchor
        self.offset_start_ms = offset_start_ms
        self.interval_to_measure_at = interval_to_measure_at

        # optional
        self.offset_end_ms = offset_end_ms

class ReoccuringDataRequirement():
    """
    A data requirement that is gathered on a timed interval beginning at the start of the Tribe Member runtime. 
    """
    def __init__(self, 
                 id: str,
                 ticker: str, 
                 interval_to_measure_at: TimeInterval, 
                 collect_every_ms: int) -> None:
        self.id = id
        self.ticker = ticker
        self.interval_to_measure_at = interval_to_measure_at,
        self.correct_every_ms = collect_every_ms

class ModelDataBlueprint():
    def __init__(self, 
                 initial_data_requirements: List[InitialDataRequirement], 
                 reoccuring_data_requirements: List[ReoccuringDataRequirement]) -> None:
        self.initial_data_requirements: List[InitialDataRequirement] = initial_data_requirements
        self.reoccuring_data_requirements: List[ReoccuringDataRequirement] = reoccuring_data_requirements