"""
TODO
This command should have the ability via options to:
1. List all current features for project by take opt for project name 
and then reading over all the directory names in /src. 
2. Create a new feature by taking an opt for feature name.
3. Delete a feature by taking an opt for feature name. 
NOTE: Feature should match the current project directory by default
and should also have the option for a project name flag to override this
default. 
"""
from .project import Project

class Feature(Project):

    def __init__(self,
                 feature_name:str,
                 custom_dep:bool):
        self.feature_name = feature_name
        self.custom_dep = custom_dep

    def create_feature(self):
        pass

    def delete_feature(self):
        pass

    def show_feature_changes(self):
        pass

    def show_feature_test_coverage(self):
        pass

def execute(args):
    pass