import shutil
import os

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def copy_directory_contents(src_dir, dst_dir, overwrite=False):
    """
    Copies the contents of one directory to another.
    
    :param src_dir: Source directory whose contents need to be copied.
    :param dst_dir: Destination directory where contents should be copied.
    :param overwrite: If True, existing files at the destination will be overwritten.
                      If False, existing files will be skipped.
    """
    if not os.path.exists(src_dir):
        raise FileNotFoundError(f"Source directory '{src_dir}' does not exist.")
    
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dst_item = os.path.join(dst_dir, item)
        
        if os.path.isdir(src_item):
            # Recursively copy directories
            shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
        else:
            if not os.path.exists(dst_item) or overwrite:
                shutil.copy2(src_item, dst_item)
                print(f"Copied '{src_item}' to '{dst_item}'")
            else:
                print(f"Skipped '{dst_item}' (already exists)")