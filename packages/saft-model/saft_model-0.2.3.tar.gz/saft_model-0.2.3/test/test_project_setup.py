
import pytest
from pathlib import Path

from saft_model.scripts.project_setup import setup_project_structure

def test_project_setup_success(tmp_path):
    project_name = "TestProject"
    model_name = "ModelName"

    setup_project_structure(project_name, model_name, tmp_path)

    project_dir: Path = tmp_path / "model"
    assert project_dir.exists() and project_dir.is_dir(), "Directory was not created."
    model_py = project_dir / "model.py"
    assert model_py.exists() and model_py.is_file(), "model.py was not successfully created"
    requirements_txt = project_dir / "requirements.txt"
    assert requirements_txt.exists() and requirements_txt.is_file(), "requirements.txt was not successfully created"
    model_data_blueprint = project_dir / "model_data_blueprint.json"
    assert model_data_blueprint.exists() and model_data_blueprint.is_file(), "model_data_blueprint.json was not successfully created"

def test_project_setup_project_name_collision_error(tmp_path):
    project_name = "TestProject"
    model_name = "ModelName"

    setup_project_structure(project_name, model_name, tmp_path)
    with pytest.raises(FileExistsError):
        setup_project_structure(project_name, model_name, tmp_path)