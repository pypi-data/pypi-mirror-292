
from . import Sentiment

class PredictionResponse():
    def __init__(self, model_id: str, time_predicted_at: int, sentiment: Sentiment, confidence: float) -> None:
        self.modelId = model_id
        self.timePredictedAt = time_predicted_at
        self.sentiment = sentiment
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "model_id": self.modelId,
            "time_predicted_at": self.timePredictedAt,
            "sentiment": self.sentiment._value_,
            "confidence": self.confidence
        }