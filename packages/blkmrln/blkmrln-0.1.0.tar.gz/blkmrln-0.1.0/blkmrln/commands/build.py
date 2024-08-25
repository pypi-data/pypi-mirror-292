import os
from ..utils import copy_directory_contents
from ..core import MinifiedBuild

def execute(args):
    """
    \nCreate directory structure of project
    \nCreate venv entry for project in venvmanager
    """
    project_name = args.name
    env_dir = args.env
    print(f"Building Project: {project_name}")
    target_root = os.path.join(os.getcwd(), project_name)
    print(f"ROOT DIR = {target_root}")
    with MinifiedBuild(project_name=project_name,
                       base_dir=os.getcwd(),
                       env_dir=env_dir) as pm:
        rebuild = pm.rebuild
        if rebuild==False:
            pm.setup_project_structure()
            
            source_dir = pm.get_resources_directory()
            print(f"Setting up project directories in {target_root}")
            copy_directory_contents(source_dir, target_root)
            print(f"Validating project directories in {target_root}")
            print(pm.validate_directories())
            print(f"Creating venv for project & installing dependencies")
            pm.create_virtual_environment()
        pm.install_requirements()
        print("Displaying State of Current Build")
        print(pm.__str__())
        print(f"Activating venv {project_name}")
        pm.activate_virtual_environment()