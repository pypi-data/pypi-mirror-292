"""
TODO
This command should be the central location where a user can interact with 
their virtual environments. 
1. User should be able to list all virtual environments and virtual environments
must be linked to /dep/common/requirements.txt for their associated project. 
EX:
venvs/projects
    -> project_1
        -| distlib==0.3.8
        -| filelock==3.15.4
        -| iniconfig==2.0.0
    -> project_2
        -| pytest==8.3.2
        -| pytest-mock==3.14.0
        -| PyYAML==6.0.2
2. User should be able to seamlessly switch between virtual environments 
by providing the project name via an opt to venvmanager. 
3. Initial setup flag with mandatory opt to define a directory outside of project 
directories for storing virtual environments. 
NOTE
This command should not handle the creation and destruction of virtual environments
as that should be heavily linked to the build step, and possibly handled in the 
/resources directory. 
"""
from ..core import Core
from pathlib import Path
from functools import reduce

class VenvManager(Core):
    def __init__(self,project_name):
        super().__init__(project_name=project_name)  

    def __str__(self) -> str:
        string_out = "\n\nVenvManager: Listing current project environments."
        venvs_path = Path(self.env_dir).parent
        for venv in venvs_path.iterdir():
            if venv.is_dir() and self.project_name and str(venv).__contains__(self.project_name):
                string_out = string_out + f"\n\t-->{venv}\t*Current Project*"
            elif venv.is_dir():
                string_out = string_out + f"\n\t-->{venv}"
            
        return string_out +"\n\n"

class VenvDepManager(VenvManager):
    def __init__(self,project_name):
        super().__init__(project_name)

    def __str__(self) -> str:
        venvManagerStr = super().__str__()
        depFiles = [x.strip() for x in venvManagerStr.split('-->')[1:]]
        venvDepFlagStr = reduce(lambda x,y: x+y,depFiles)
        return venvDepFlagStr

def execute(args):
    project_name = args.project
    dep_flag = args.dep_flag
    if dep_flag:
        with VenvDepManager(project_name) as vm:
            print(vm.__str__())
        return
    with VenvManager(project_name) as vm:
        print(vm.__str__())