"""
labrador - _approach
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import os
import typer
from rich.prompt import Prompt
from typing_extensions import Annotated
from .decorators import in_work_package
from .utils import sanitize, list_approaches
from .documentation import init_doc


app = typer.Typer()


@app.command()
@in_work_package
def create(name: Annotated[str, typer.Option(prompt="🛬 New approach name")]):
    """
    Creates a new approach in this work-package
    """
    # we are in a work-package, so cwd is correct
    existing_approaches = list_approaches(os.getcwd())
    folder_name = str(len(existing_approaches) + 1).zfill(2) + "_" + sanitize(name)
    os.mkdir(folder_name)
    os.chdir(folder_name)
    # initialize the documentation
    description = Prompt.ask(default="Write a short description for your approach")
    init_doc(description=description)
