
def format_proper_name_to_pascal_case(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_') if word).replace("-", "").replace(" ", "")
        

def format_template_file(project_name: str, model_name: str):

    formatted_project_name = format_proper_name_to_pascal_case(project_name)
    formatted_model_name = format_proper_name_to_pascal_case(model_name)

    model_implementation_file_template = """
# ------------------------------------------------------------------------------------------
# SAFT MODEL PROJECT
#
# PROJECT NAME: {project_name}
# MODEL NAME: {model_name}
# ------------------------------------------------------------------------------------------


from saft_model.classes import SAFTModelClass
from saft_model.classes.InputData import InputData  
from saft_model.classes.PredictionResponse import PredictionResponse

class {model_name}(SAFTModelClass):
    def predict(self, data_input: InputData) -> PredictionResponse:
        return None

    """.format(
            project_name=formatted_project_name,
            model_name=formatted_model_name
        )
    return model_implementation_file_template