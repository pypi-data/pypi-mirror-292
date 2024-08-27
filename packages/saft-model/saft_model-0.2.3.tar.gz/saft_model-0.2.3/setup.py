from setuptools import setup, find_packages
import os

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='saft_model',
    version='0.2.3',
    packages=find_packages(),
    include_package_data=True,
    # package_data={
    #     '': ['data/*.txt'],
    # },
    install_requires=[

    ],
    entry_points={
        "console_scripts": [
            "create-saft-project = saft_model:project_setup_prompt"
        ]
    },
    long_description=description,
    long_description_content_type="text/markdown"
)
