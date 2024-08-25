from ..core import Core
from .project import Project
from .feature import Feature
from abc import ABCMeta, abstractmethod


class Test(Core):
    __metaclass__ = ABCMeta
    def __init__(self,
                 test_type:str):
        self.test_type = test_type

    @abstractmethod
    def run_tests(self,scope:str,scope_name:str):
        pass

    @abstractmethod
    def get_coverage(self,scope:str,scope_name:str):
        pass

class TestProject(Test):
    def __init__(self, 
                 TestableProject: Project,
                 test_type: str):
        super().__init__(test_type)
        self.TestProject = TestableProject
        self.project_coverage = self.get_coverage()
    
    def run_tests(self, scope: str, scope_name: str):
        """
        Run tests at project scope
        """
        return super().run_tests(scope, scope_name)

    def get_coverage(self, scope: str, scope_name: str):
        """
        Get project test coverage
        """
        return super().get_coverage(scope, scope_name)

class TestFeature(TestProject):
    def __init__(self, 
                 TestableProject: Project, 
                 TestableFeature: Feature,
                 test_type: str):
        super().__init__(TestableProject, test_type)
        self.TestableFeature = TestableFeature
        self.feature_coverage = self.get_coverage()
    
    def run_tests(self, scope: str, scope_name: str):
        """
        Run tests at feature scope
        """
        return super().run_tests(scope, scope_name)

    def get_coverage(self, scope: str, scope_name: str):
        """
        Get feature test coverage
        """
        return super().get_coverage(scope, scope_name)

def execute(args):
    pass