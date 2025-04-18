import os

def get_project_root() -> str:
    """
    Get the root directory of the project.
    """
    
    current_file = os.path.abspath(__file__)
    common_dir = os.path.dirname(current_file)
    src_dir = os.path.dirname(common_dir)
    project_root = os.path.dirname(src_dir)
    
    return project_root