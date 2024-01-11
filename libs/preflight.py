#Version 1/4/24
import inspect
import os
from openpyxl import load_workbook

class CheckExcelFiles:
    def __init__(self, lst_files, lst_shts, errs):
        """
        Initialize CheckExcelFiles with a list of file paths and a list of sheets.
        JDL 1/2/24
        """
        self.lst_files = lst_files # list of file paths to check
        self.lst_shts = lst_shts # list of lists of sheets

        self.wb = None # Current Excel workbook object
        self.IsWbErr = False # Flag if any errors during procedure

        # ErrorHandle instance and atts - Errors are treated as non-fatal warnings
        self.errs = errs
        self.errs.IsWarning = True
        self.errs.IsPrint = False

    def CheckFilesProcedure(self):
        """
        Procedure to check specified Excel files and sheets
        JDL 1/4/24
        """
        # Set location for looking up error messages
        self.errs.Locn = current_fn()

        for idx in range(len(self.lst_files)):
            self.IsWbErr = False

            # Check that file exists and can be opened; set self.wb object
            if not self.ExcelFileExists(idx): continue
            if not self.ExcelFileOpens(idx): continue

            # If valid Excel file, check if specified sheets are present
            if self.AllSheetsExist(idx): self.wb.Close(False)

    def ExcelFileExists(self, idx):
        """
        Check if each Excel file exists and if each sheet exists in the file.
        JDL 1/4/24
        """
        fpath = self.lst_files[idx]
        if self.errs.is_fail(not os.path.exists(fpath), 1, '\n ' + fpath + '\n'):
            self.IsWbErr = True
            self.errs.RecordErr()
            return False
        return True

    def ExcelFileOpens(self, idx):
        """
        Check if each Excel file exists and if each sheet exists in the file.
        JDL 1/4/24
        """
        fpath = self.lst_files[idx]
        try:
            self.wb = load_workbook(filename=fpath)
            return True
        except Exception as e:
            self.IsWbErr = True
            self.errs.is_fail(True, 2, '\n ' + fpath + '\n')
            self.errs.RecordErr()
            return False

    def AllSheetsExist(self, idx):
        """
        Iteratively check if specified sheets exist in self.wb
        JDL 1/4/24
        """
        for sheet_name in self.lst_shts[idx]:
            if not self.SheetExists(idx, sheet_name): break

    def SheetExists(self, idx, sheet_name):
        """
        Check if specified sheet exists in self.wb
        JDL 1/4/24
        """
        #Set the path and errParam string for current file and sheet
        fpath = self.lst_files[idx]
        errParam = '\n Missing: ' + sheet_name + ' in ' + fpath + '\n'

        #Check if sheet exists in self.wb
        is_sht_exists = sheet_name in self.wb.sheetnames
        if self.errs.is_fail(not is_sht_exists, 3, errParam):
            self.IsWbErr = True
            self.errs.RecordErr()
            return False
        return True

def current_fn():
    """
    Return the name of the current function
    JDL 1/4/24
    """
    return inspect.currentframe().f_back.f_code.co_name