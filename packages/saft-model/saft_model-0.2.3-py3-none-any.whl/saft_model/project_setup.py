
import os
from .templates.model_implementation_file import format_template_file as mdl_fmt

def setup_project_structure():
    # get relevant information 
    project_name = input("Enter the project name: ")
    model_name = input("Enter the model name: ")

    # make project structure
    try:
        os.makedirs(project_name)
        print(f"Directory '{project_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{project_name}' already exists.")

    model_file_path = os.path.join(project_name, 'model.py')

    with open(model_file_path, 'w') as model_file:
        model_file.write(mdl_fmt(project_name, model_name))

        print(f"File 'model.py' created successfully in '{project_name}'.")

    requirements_path = os.path.join(project_name, 'requirements.txt')
    with open(requirements_path, 'w'): pass

    model_data_blueprint = os.path.join(project_name, 'model_data_blueprint.json')
    with open(model_data_blueprint, 'w'): pass

    