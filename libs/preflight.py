#Version 1/4/24
import pandas as pd
import os
from openpyxl import load_workbook
import util


class CheckDataFrame:
    def __init__(self, df, errs):
        """
        Initialize CheckDataFrame with df and errs ErrorHandle instance as attributes.
        JDL 1/11/24
        """
        self.df = df
        self.errs = errs

    def NoDuplicateCols(self):
        """
        Check if the DataFrame self.df does not have duplicate column names
        JDL 1/11/24
        """
        # Get the DataFrame columns
        cols = self.df.columns
        
        # Check if there are duplicate column names
        if cols.is_unique: return True
        duplicates = cols[cols.duplicated()].unique()
        ErrParam = "\nDuplicate columns: " + ', '.join(map(str, duplicates))
        if self.errs.is_fail(True, 1, util.current_fn(), ErrParam): self.errs.RecordErr()
        return False
    
    def ColumnsContainListVals(self, list_vals):
        """
        Check if the DataFrame columns contain a specified list of values
        JDL 1/11/24
        """
        # Loop through each value in list_vals and check if it is in the DataFrame columns
        for val in list_vals:
            if val not in self.df.columns:
                ErrParam = '\nMissing: ' + str(val)
                if self.errs.is_fail(True, 1, util.current_fn(), ErrParam): self.errs.RecordErr()
                return False
        return True

    def IndexContainsListVals(self, list_vals):
        """
        Check if the DataFrame index contains a specified list of values
        JDL 1/11/24
        """
        # Loop through each value in list_vals and check if it is in the DataFrame index
        for val in list_vals:
            if val not in self.df.index:
                ErrParam = '\nMissing: ' + str(val)
                if self.errs.is_fail(True, 1, util.current_fn(), ErrParam): self.errs.RecordErr()
                return False
        return True
    
    def ColAllPopulated(self, col_name):
        """
        Check if all values in a specified column are non-null
        JDL 1/11/24
        """
        # Check if column contains any null values and report error if so
        if not self.df[col_name].isna().any(): return True
        if self.errs.is_fail(True, 1, util.current_fn(), col_name): self.errs.RecordErr()
        return False
    
    def ColAllNumeric(self, col_name):
        """
        Check if values in a specified column are non-blank and numeric
        JDL 1/11/24
        """
        # Convert the column to numeric, coercing non-numeric values to NaN
        col_numeric = pd.to_numeric(self.df[col_name], errors='coerce')

        # Check if there are any NaN values
        is_col_all_numeric = not col_numeric.isna().any()
        if self.errs.is_fail((not is_col_all_numeric), 1, util.current_fn(), col_name):
            self.errs.RecordErr()
            return False
        return True
    
    def ContainsRequiredCols(self, cols_req):
        """
        Check if .df contains a specified list of column names
        JDL 1/11/24
        """
        #Check df has all required columns
        for col in cols_req:
            if self.errs.is_fail((not col in self.df.columns), 1, util.current_fn(), col):
                self.errs.RecordErr()
                return False
        return True

    def ColNonBlank(self, col_name):
        """
        Check if specified column contains any non-blank values
        JDL 1/11/24
        """
        #Check column contains at least one non-blank value
        is_col_nonblank = self.df[col_name].notnull().any()
        if self.errs.is_fail((not is_col_nonblank), 1, util.current_fn(), col_name):
            self.errs.RecordErr()
            return False
        return True

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
        self.errs.Locn = util.current_fn()

        for idx in range(len(self.lst_files)):
            self.IsWbErr = False

            # Check that file exists and can be opened; set self.wb object
            if not self.ExcelFileExists(idx): continue
            if not self.ExcelFileOpens(idx): continue

            # If valid Excel file, check if specified sheets are present
            if self.AllSheetsExist(idx): self.wb.Close(False)

    def ExcelFileExists(self, idx):
        """
        Check if an Excel file exists based on specified list index for list 
        of files to check (iteration over list in calling CheckFilesProcedure)
        JDL 1/4/24
        """
        #If error, use .is_fail to set params including Locn of calling function
        fpath = self.lst_files[idx]
        sFPath = '\n ' + fpath + '\n'
        if self.errs.is_fail(not os.path.exists(fpath), 1, self.errs.Locn, sFPath):
            self.IsWbErr = True
            self.errs.RecordErr()
            return False
        return True

    def ExcelFileOpens(self, idx):
        """
        Check if file is a valid Excel file based on ability to open
        JDL 1/4/24
        """
        fpath = self.lst_files[idx]
        try:
            self.wb = load_workbook(filename=fpath)
            return True
        
        #If error, use .is_fail to set params including Locn of calling function
        except Exception as e:
            self.IsWbErr = True
            self.errs.is_fail(True, 2, self.errs.Locn, '\n ' + fpath + '\n')
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
        if self.errs.is_fail(not is_sht_exists, 3, self.errs.Locn, errParam):
            self.IsWbErr = True
            self.errs.RecordErr()
            return False
        return True