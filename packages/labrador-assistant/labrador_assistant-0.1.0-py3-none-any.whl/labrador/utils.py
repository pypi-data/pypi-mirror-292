"""
labrador - utils
Author :    Calixte Mayoraz
Copyright : (c) 2024
"""
import re
import os
from builtins import sorted

from unidecode import unidecode


def get_project_root() -> 'str | None':
    """
    Finds the project that the CLI is currently in by checking at each level if a .lab exists.
    Returns the path of the project if the CLI's cwd is in a project, and None otherwise.

    Returns
    -------
    str | None :
        the path of the root of the project
    """
    cwd = os.getcwd().split(os.path.sep)
    for level in range(len(cwd)):
        if level == 0:
            lab_path = os.path.join(os.getcwd(), ".lab")
        else:
            lab_path = os.path.join(os.path.sep.join(cwd[:-level]), ".lab")
        if os.path.exists(lab_path):
            return os.path.split(lab_path)[0]
    return None


def sanitize(string: str) -> 'str':
    """
    Returns a sanitized version of the input string with the following convention guidelines:
     - all non-alphanumeric characters are replaced with underscores
        - consecutive characters are replaced with a single underscore
     - all accents are sanitized with unidecode
     - all lowercase.
     - leading and tailing characters are alphanumeric

    Examples
    --------
    >>> sanitize("Project #1 - Manhattan")
    'project_1_manhattan'
    >>> sanitize("HELLO! my n4me is ... I forget!")
    'hello_my_n4me_is_i_forget'
    >>> sanitize("01 - numbers in front work.")
    '01_numbers_in_front_work'
    >>> sanitize("...with_punctuation in FRONT and in BACK!!!")
    'with_punctuation_in_front_and_in_back'

    Parameters
    ----------
    string: the string to sanitize

    Returns
    -------
    sanitized: str
    """
    return re.sub('[^0-9a-z]+', " ", unidecode(string).lower()).strip().replace(" ", "_")


def unsanitize(sanitized_name: str) -> 'str':
    """
    Attempts to reverse the `sanitize` method by doing the following:
     - split by underscores
     - capitalize each word
     - remove any leading zeroes
     - joining split words with spaces

    Examples
    --------
    >>> unsanitize("01_manhattan_project")
    '1 Manhattan Project'
    >>> unsanitize("hello_i_am_a_frog")
    'Hello I Am A Frog'

    Parameters
    ----------
    sanitized_name: str
        the string to un-sanitize

    Returns
    -------
    str : the unsanitized string
    """
    return " ".join(map(lambda x: re.sub('^0+', '', x.capitalize()), sanitized_name.split("_")))


def __is_valid_wp_or_approach(path: str):
    if not os.path.isdir(path):
        return False
    return re.fullmatch('[0-9]{2}_', os.path.split(path)[-1][:3]) is not None


def list_work_packages() -> 'list[str]':
    """
    returns the valid work-package names within the current project. This assumes that we currently
    are within a project.

    A work-package name is considered "valid" if it meets the following criteria:
        - it is a folder
        - it starts with two numbers and an underscore

    Returns
    -------
    list[str]:
        the valid work-package names in the project
    """
    root = get_project_root()
    work_packages = map(lambda element: os.path.join(root, element), os.listdir(root))
    return sorted(filter(__is_valid_wp_or_approach, work_packages))


def list_approaches(work_package_path) -> 'list[str]':
    """
    Returns a list of valid approaches in the given work-package path. This assumes that we are
    currently in a work-package. If not, will return an empty list. An approach name is
    considered "valid" if all the following criteria are met:
        - it is a folder
        - it starts with two numbers and an underscore

    Parameters
    ----------
    work_package_path: str
        the valid path to a work-package to check.

    Returns
    -------
    list[str]:
        the valid approach names in the work-package.
    """
    approaches = map(
        lambda element: os.path.join(work_package_path, element),
        os.listdir(work_package_path)
    )
    return sorted(filter(__is_valid_wp_or_approach, approaches))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
