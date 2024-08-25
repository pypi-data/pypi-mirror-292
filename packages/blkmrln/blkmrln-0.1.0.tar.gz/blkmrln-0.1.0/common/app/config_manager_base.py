from os import environ
from pathlib import Path
import logging
import yaml

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseConfigManager(object):
    def __init__(self):
        self._configuration = self.get_config()
    
    def get_config(self,
                   config_path:None|str=None)->dict:
        if config_path==None:
            config_path = Path()\
                .resolve()\
                / 'config' / environ['PROJECT_NAME'] / 'secrets' / 'config.yaml'
        with open(config_path, 'r') as file:
            configuration = yaml.safe_load(file)
        return configuration
    
    def get_logger(self,
                   enabled:bool,
                   name="Default")->logging.Logger|None:
        """
        Returns a configured logger.

        Parameters:
        - enabled (bool): If logging is enabled. 
        - name (str): The name of the logger.
        - level (int): The log level for the logger (e.g., logging.INFO, logging.DEBUG).
        - console_output (bool): Whether to add a console handler.

        Returns:
        - logging.Logger: Configured logger.
        - None if logging is disabled.
        """
        if enabled:
            level = self._env_configuration['log']['level']
            logger = logging.getLogger(name)
            logger.setLevel(level)

            # Remove existing handlers
            if logger.hasHandlers():
                logger.handlers.clear()
            
            # Create console handler
            ch = logging.StreamHandler()
            ch.setLevel(level)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            return logger
        return None
    
    def get_db_cxn(self,
                   local=True,
                   **kwargs):
        pass