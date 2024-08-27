
from typing import List, Optional

from saft_model.Sentiment import Sentiment

class DataPredictionRequirement():
    def __init__(self,
                 id: str) -> None:
        self.id = id

class InitialDataPredictionRequirement(DataPredictionRequirement):
    def __init__(self,
                 id: str) -> None:
        super().__init__(id)

class ReoccuringDataPredictionRequirement(DataPredictionRequirement):
    def __init__(self,
                 id: str,
                 num_measurements_needed: int,
                 require_consecutive: bool) -> None:
        super().__init__(id)
        self.num_measurements_needed = num_measurements_needed
        self.require_consecutive = require_consecutive

class TradeResolution():
    def __init__(self,
                 by_end_of_hours: bool,
                 static_time: Optional[int] = None,
                 stop_loss_pct: Optional[int] = None) -> None:
        self.by_end_of_hours = by_end_of_hours
        self.static_time = static_time
        self.stop_loss_pct = stop_loss_pct

class PredictionTrigger():
    def __init__(self,
                 on_classification: Sentiment,
                 minimum_confidence_needed: int,
                 resolve_on: TradeResolution) -> None:
        self.on_classification = on_classification
        self.minimum_confidence_needed = minimum_confidence_needed
        self.resolve_on = resolve_on
 
class TradingStrategy():
    def __init__(self,
                 timezone: str,
                 start_time: str,
                 end_time: str,
                 prediction_data_requirements: List[DataPredictionRequirement],
                 prediction_triggers: List[PredictionTrigger]) -> None:
        self.timezone = timezone
        self.start_time = start_time
        self.end_time = end_time
        self.prediction_data_requirements = prediction_data_requirements
        self.prediction_triggers = prediction_triggers
