
import os
import json
from pathlib import Path
from InquirerPy import prompt

from .templates.model_implementation_file import format_template_file as mdl_fmt
from .templates.model_blueprint import model_data_blueprint_template as data_blueprint_fmt

def project_setup_prompt():
    """Entrypoint script for users to setup their file structures
    
    """
    print("---------------------------------------------------------------------")
    print("     SAFT MODEL PROJECT SETUP")
    print("---------------------------------------------------------------------")
    questions = [
        {"type": "input", "message": "Project Name:", "name": "project_name"},
        {"type": "input", "message": "Model Name:", "name": "model_name"},
        {"type": "filepath", "message": "Where do you want to make this project", "name": "project_path", "default": "."},
        {"type": "confirm", "message": "Confirm?", "name": "confirm", "default": False},
    ]
    result = prompt(questions)
    project_name = result["project_name"]
    model_name = result["model_name"]
    project_path = Path(result["project_path"])
    
    if result["confirm"] == True:
        print("Project setup confirmed. Creating project...")
        setup_project_structure(project_name, model_name, project_path)



def setup_project_structure(project_name: str, model_name: str, path: Path):
    """Creates a standard saft project file structure

    Args:
        project_name: string name of project
        model_name: string name of the model
        path: path to file location

    Raises:
        FileExistsError: If the path ends in a location where there is already a directory matching what would be created
                         the operation will be canceled
    """

    project_dir = path / "model"

    if project_dir.exists():
        raise FileExistsError(f"Directory '{project_dir}' already exists. Cannot create project")

    project_dir.mkdir(parents=True)
    print(f"Directory '{project_dir}' created successfully.")
    

    model_file_path = project_dir / 'model.py'

    with open(model_file_path, 'w') as model_file:
        model_file.write(mdl_fmt(project_name, model_name))

        print(f"File 'model.py' created successfully in '{project_name}'.")

    requirements_path = project_dir / 'requirements.txt'
    with open(requirements_path, 'w'): pass

    model_data_blueprint_path = project_dir / 'model_data_blueprint.json'
    with open(model_data_blueprint_path, 'w') as out_file:
        json.dump(data_blueprint_fmt, out_file)
    
