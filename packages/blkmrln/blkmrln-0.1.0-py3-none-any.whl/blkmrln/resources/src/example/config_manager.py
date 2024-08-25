from ...common.app.config_manager_base import Singleton, BaseConfigManager

class ConfigManager(BaseConfigManager):
    __metaclass__=Singleton
    
    def __init__(self,
                 logging_enabled:bool,
                 local:bool,
                 config_path:str|None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.logger = self.get_logger(enabled=logging_enabled)
            self.secrets = self.get_config(config_path=config_path)
            self.db_cxn = self.get_db_cxn(local=local)

    def get_db_cxn(self, local=True, **kwargs):
        """
        Morty (You): Ahh jeez Rick I didn't realize you could 
        override the method so easily
        Rick: Ooof*burp*fff courssee you cann MooRRRTTYY don't
        be an id*burp*iootttt
        """
        super().get_db_cxn(local, **kwargs)
        if local==False:
            user = self._configuration['db']['user']
            db_pass = self._configuration['db']['pass']
        return None