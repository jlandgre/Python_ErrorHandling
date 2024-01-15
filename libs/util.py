import inspect

def current_fn():
    """
    Return name of the calling function (.f_back attribute)
    JDL 1/4/24
    """
    return inspect.currentframe().f_back.f_code.co_name