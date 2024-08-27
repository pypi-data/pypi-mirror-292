"""ModelTemplateClass.py 

A template (interface-like) class for defining the expected methods of a model
NOTE: Every model will be a sub-class of this class
"""

from abc import ABC, abstractmethod

from saft_model.ModelDataBlueprint import ModelDataBlueprint
from saft_model.PredictionResponse import PredictionResponse
from saft_model.InputData import InputData

class SAFTModelClass(ABC):
    @abstractmethod
    def predict(self, prediction_input: InputData) -> PredictionResponse:
        """
        Takes in dictionary of data points for prediction,
        returns a prediction response object
        """
        return None