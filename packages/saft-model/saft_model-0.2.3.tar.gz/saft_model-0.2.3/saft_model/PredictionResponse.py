
from saft_model.Sentiment import Sentiment

class PredictionResponse():
    def __init__(self, time_predicted_at: int, sentiment: Sentiment, confidence: float) -> None:
        self.timePredictedAt = time_predicted_at
        self.sentiment = sentiment
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "time_predicted_at": self.timePredictedAt,
            "sentiment": self.sentiment._value_,
            "confidence": self.confidence
        }