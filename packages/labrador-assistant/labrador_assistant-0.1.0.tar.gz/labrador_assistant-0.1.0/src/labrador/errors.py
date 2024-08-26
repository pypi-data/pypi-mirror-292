"""
labrador - errors
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""


class AlreadyInProject(Exception):
    """
    If we are already in a project and need to create one
    """


class NotInProject(Exception):
    """
    If we are not in a project and need to be in one.
    """


class NotAtProjectRoot(Exception):
    """
    If we are not at the project root
    """


class NotInWorkPackage(Exception):
    """
    If we are not in a work-package and we need to be in one.
    """


class ProjectExists(Exception):
    """
    If we wanted to create a project folder but it already exists.
    """
