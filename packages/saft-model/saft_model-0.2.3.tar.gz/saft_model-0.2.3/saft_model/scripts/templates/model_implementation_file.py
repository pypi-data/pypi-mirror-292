
import re

# def format_proper_name_to_pascal_case(name: str) -> str:
#     split_name = 
#     return ''.join(x for x in name.title() if not x.isspace())
#     # return ''.join(word for word in name.split('_') if word).replace("-", "").replace(" ", "")
#     s = re.sub(r'[^a-zA-Z0-9]', ' ', s)
#     # Split the string by spaces and capitalize each word
#     words = s.split()
#     pascal_case = ''.join(word.capitalize() for word in words)
#     formatted_word = ''.join(word for word in pascal_case.split('_') if word).replace("-", "").replace(" ", "")
#     return formatted_word
        

def format_template_file(project_name: str, model_name: str):

    formatted_project_name = project_name
    formatted_model_name = model_name

    model_implementation_file_template = """
# ------------------------------------------------------------------------------------------
# SAFT MODEL PROJECT
#
# PROJECT NAME: {project_name}
# MODEL NAME: {model_name}
# ------------------------------------------------------------------------------------------

from saft_model.SAFTModelClass import SAFTModelClass
from saft_model.InputData import InputData  
from saft_model.PredictionResponse import PredictionResponse
from saft_model.Sentiment import Sentiment

import random 
from datetime import datetime


def get_random_correct_sentiment():
    rand_num = random.choice([0, 2])
    if rand_num == 0: return Sentiment.BULLISH
    elif rand_num == 1: return Sentiment.BEARISH
    else: return Sentiment.NEUTRAL

def get_random_confidence_level():
    return random.random()

class {model_name}(SAFTModelClass):
    def predict(self, data_input: InputData) -> PredictionResponse:
        return PredictionResponse(
            int(datetime.now().timestamp() * 1000),
            get_random_correct_sentiment(),
            get_random_confidence_level()
        )

    """.format(
            project_name=formatted_project_name,
            model_name=formatted_model_name
        )
    return model_implementation_file_template