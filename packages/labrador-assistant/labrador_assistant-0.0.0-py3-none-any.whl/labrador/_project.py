"""
labrador - _project
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import os.path
import pytoml as toml
import typer
from typing_extensions import Annotated
from rich.prompt import Prompt
from .decorators import in_project, not_in_project
from .documentation import init_doc, create_report
from .errors import ProjectExists
from .utils import sanitize

app = typer.Typer()


def __create_lab_file(project_name: str):
    """
    Creates a .lab file with the necessary information about the current lab project at the
    current working directory.

    Parameters
    ----------
    project_name
    """
    with open(".lab", "w", encoding="utf-8") as outfile:
        toml.dump({
            "project": {
                "name": project_name
            }
        }, outfile)


@app.command()
@not_in_project
def init():
    """
    Initializes the current directory as a labradar project.

    Raises
    ------
    AlreadyInProject
        if this folder or any parent folder is a labradar project
    """
    name = os.path.split(os.getcwd())[-1]
    __create_lab_file(name)
    description = Prompt.ask(default="Write a short description for your project")
    init_doc(description=description)


@app.command()
def create(name: Annotated[str, typer.Option(prompt="🔬 New lab project name")]):
    """
    Creates a new labradar project. This will create a new folder (with a sanitized name),
    add the .lab metadata and README.md files inside.

    Parameters
    ----------
    name: the name to give to the project. This name will be sanitized to have a clean folder name.
    """
    folder_name = sanitize(name)
    if os.path.exists(folder_name):
        raise ProjectExists(f"Project folder {folder_name} already exists!")
    os.mkdir(folder_name)
    os.chdir(folder_name)
    __create_lab_file(name)
    description = Prompt.ask(default="Write a short description for your project")
    init_doc(description=description)


@app.command()
@in_project
def report():
    """
    Generates a full report for the current project
    """
    create_report()
