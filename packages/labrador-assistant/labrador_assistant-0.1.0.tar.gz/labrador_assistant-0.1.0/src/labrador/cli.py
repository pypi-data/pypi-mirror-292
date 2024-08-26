"""
labrador - __init__.py
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import typer
from ._approach import app as approach_cli
from ._project import app as project_cli
from ._work_package import app as wp_cli

app = typer.Typer()
app.add_typer(project_cli, name="project", help="Project-related commands")
app.add_typer(wp_cli, name="wp", help="Work-Package-related commands")
app.add_typer(approach_cli, name="approach", help="Approach-related commands")
