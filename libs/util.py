import inspect
import os

def ck_for_shorten_path(fpath, max_len):
    """
    Return a shortened version of the file path
    JDL 1/4/24
    """
    if len(fpath.split(os.sep)) > max_len:
        return os.sep.join(fpath.split(os.sep)[-max_len:])
    return fpath

def current_fn():
    """
    Return name of the calling function (.f_back attribute)
    JDL 1/4/24
    """
    return inspect.currentframe().f_back.f_code.co_name