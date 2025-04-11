import os

def get_project_root() -> str:
    """
    Get the root directory of the project.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))