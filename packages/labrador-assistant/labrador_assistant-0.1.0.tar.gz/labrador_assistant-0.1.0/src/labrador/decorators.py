"""
labrador - decorators
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import functools
import os.path

from .errors import (
    NotInProject,
    AlreadyInProject,
    NotAtProjectRoot,
    NotInWorkPackage
)
from .utils import get_project_root


def in_project(func):
    """
    Decorator to ensure that we are in a project

    Raises
    ------
    NotInProject
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if get_project_root() is None:
            raise NotInProject()
        return func(*args, **kwargs)
    return wrapped


def not_in_project(func):
    """
    Decorator to ensure we are NOT in a project

    Raises
    ------
    AlreadyInProject
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        root = get_project_root()
        print("pouet", root)
        if root is not None:
            raise AlreadyInProject(f"You are already in a project at {root}.")
        return func(*args, **kwargs)
    return wrapped


def in_work_package(func):
    """
    Asserts that we are at a level directly below a project root, i.e. in a work-package.

    Raises
    ------
    NotInWorkPackage
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not os.path.exists(os.path.abspath(os.path.join(os.getcwd(), '..', '.lab'))):
            raise NotInWorkPackage()
        return func(*args, **kwargs)
    return wrapped


def at_project_root(func):
    """
    Asserts that we are at the root-level of the project.

    Raises
    ------
    NotAtProjectRoot
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not os.path.exists(os.path.abspath(os.path.join(os.getcwd(), '.lab'))):
            raise NotAtProjectRoot()
        return func(*args, **kwargs)
    return wrapped
