"""
labrador - _work_package
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import os
import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from .decorators import in_project, get_project_root
from .utils import list_work_packages, sanitize
from .documentation import init_doc


app = typer.Typer()


@app.command()
@in_project
def create(name: Annotated[str, typer.Option(prompt="📦 New work-package name")]):
    """
    Create a new work-package folder. The folder name will be sanitized and prepended with a ##_
    given then number of work-packages already within the project.

    Parameters
    ----------
    name : str
        the name of the work-package to add.
    """
    root = get_project_root()
    existing_wps = list_work_packages()
    folder_name = str(len(existing_wps) + 1).zfill(2) + "_" + sanitize(name)
    wp_folder = os.path.join(root, folder_name)
    os.mkdir(wp_folder)
    print(f"Created work package {name} at {folder_name}")
    description = Prompt.ask(default="Write a short description for your work-package")
    init_doc(wp_folder, description=description)
