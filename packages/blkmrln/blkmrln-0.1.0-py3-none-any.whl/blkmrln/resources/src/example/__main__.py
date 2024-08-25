from dataclasses import dataclass
from src.example.config_manager import ConfigManager
import getopt
import sys

@dataclass
class EntryPoint:
    local: bool = True
    config_path: str = None
    logging_enabled: bool = False

def entrypoint(argv)->None:
    try:
        opts, args = getopt.getopt(argv, "hlti:", ["help", "logging", "test","input_config="])
    except getopt.GetoptError as err:
        print(str(err))
        print("\nUsage: python -m example [-h] [-l] [-t] [--input=FILEPATH]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage: python -m example [-h] [-l] [-t] [--input=FILEPATH]")
            sys.exit()
        elif opt in ("-i", "--input"):
            settings.config_path = arg
        elif opt in ("-l", "--logging"):
            settings.logging_enabled = True
        elif opt in ("-t", "--testing"):
            settings.local = True
    return

if __name__ == "__main__":
    settings = EntryPoint()
    entrypoint(sys.argv[1:])
    program_manager = ConfigManager(settings.logging_enabled,settings.local,settings.config_path)
    print(program_manager.logger)
    print(program_manager.secrets)
    print(program_manager.db_cxn)
