#Version 1/3/24
import pandas as pd
import inspect
import os

class CheckExcelFiles:
    def __init__(self, lst_files, lst_shts, errs):
        """
        Initialize CheckExcelFiles with a list of file paths and a list of sheets.
        JDL 1/2/24
        """
        self.lst_files = lst_files
        self.lst_shts = lst_shts

        self.errs = errs
        self.errs.IsWarning = True
        self.errs.IsPrint = False

    def ExcelFileExists(self, errs):
        """
        Check if each Excel file exists and if each sheet exists in the file.
        JDL 1/3/24
        """
        self.errs.Locn = current_fn()

        # Iterate over each file in the list
        for fpath in self.lst_files:
            f = SplitPath(fpath)[1]

            # Check if the file exists
            if self.errs.is_fail(not os.path.exists(fpath), 1, f):
                self.errs.RecordErr()

        # Print the accumulated error messages
        if len(errs.Msgs_Accum) > 0: print('\n\n', errs.Msgs_Accum + '\n')


def SplitPath(filepath):
    """
    Split a file path into directory path and file name.
    JDL 1/3/24
    """
    path, f = os.path.split(filepath)
    return path, f


def current_fn():
    return inspect.currentframe().f_back.f_code.co_name