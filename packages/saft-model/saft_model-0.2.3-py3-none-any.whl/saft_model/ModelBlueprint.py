
from saft_model.TradingStrategy import TradingStrategy
from saft_model.ModelDataBlueprint import ModelDataBlueprint

class ModelBlueprint():
    def __init__(self,
                 trading_strategy: TradingStrategy,
                 data_blueprint: ModelDataBlueprint) -> None:
        self.trading_strategy = trading_strategy
        self.data_blueprint = data_blueprint