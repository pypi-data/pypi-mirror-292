"""
TODO
This command should control black formatting for the repository and should 
be built to:
1. Format the entire project
2. Format a subfolder of the project. 
3. Show formatted and unformatted code by:
    a. Project
    b. Feature
NOTE
The default project selection should be the current directory IF the current
directory is a project directory. Otherwise this command should require the 
user to provide a project name via opt. 
"""
from ..core import Core
from .project import Project
from .feature import Feature
from abc import ABCMeta, abstractmethod


class Format(Core):
    __metaclass__ = ABCMeta
    def __init__(self):
        pass

    @abstractmethod
    def run_formatter(self,scope:str,scope_name:str):
        """
        Abstract method to run formatter
        Requires scope and target
        """
        pass

    @abstractmethod
    def get_coverage(self,scope:str,scope_name:str):
        """
        Abstract method to get formatter coverage
        Requires scope and target
        """
        pass

class FormatProject(Format):
    def __init__(self, 
                 TestableProject: Project,
                 test_type: str):
        super().__init__(test_type)
        self.TestProject = TestableProject
        self.project_coverage = self.get_coverage()
    
    def run_formatter(self, scope: str, scope_name: str):
        """
        Run project formatter
        """
        return super().run_formatter(scope, scope_name)

    def get_coverage(self, scope: str, scope_name: str):
        """
        Get project formatter coverage
        """
        return super().get_coverage(scope, scope_name)

class FormatFeature(FormatProject):
    def __init__(self, 
                 TestableProject: Project, 
                 TestableFeature: Feature,
                 test_type: str):
        super().__init__(TestableProject, test_type)
        self.TestableFeature = TestableFeature
        self.feature_coverage = self.get_coverage()
    
    def run_formatter(self, scope: str, scope_name: str):
        """
        Run feature formatter
        """
        return super().run_formatter(scope, scope_name)

    def get_coverage(self, scope: str, scope_name: str):
        """
        Get feature formatter coverage
        """
        return super().get_coverage(scope, scope_name)

def execute(args):
    pass