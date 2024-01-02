import inspect

class DemoClass():
    def __init__(self):
        self.x = 6

    def run_checks(self, errs):
        """
        Run all checks
        JDL 1/2/24
        """
        errs.Locn = inspect.currentframe().f_code.co_name
        is_pass = True

        # Fatal error
        if errs.is_fail(errs, True, 1): return errs.IsErr

        return False