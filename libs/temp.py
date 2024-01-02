import pandas as pd
import os

iErrNotFound = 10000

class ErrorHandle:
    def __init__(self, libs_dir, IsHandle=True):
        self.IsHandle = IsHandle

        self.Locn = ""  # Function where error occurred
        self.iCodeLocal = 0 # Local, integer error code
        self.iCodeBase = 0  # Base error code for .Locn lookup
        self.iCodeReport = 0 # Lookup code for error message (Base + Local)
        self.ErrParam = None
        self.ErrMsg = ''
        self.IsNewErr = True
        self.IsErr = False
        self.df_errs = pd.read_excel(libs_dir + 'ErrorCodes.xlsx', sheet_name='Errors_')

    def GetBaseErrCode(self):
        """
        Set base error code based on location.
        JDL 1/2/24
        """
        # If location not in errors, set base code to not found
        if self.Locn not in self.df_errs['Locn'].values:
            self.iCodeBase = iErrNotFound
        else:
            # Get rows with matching location and 'Base' message
            fil = (self.df_errs['Locn'] == self.Locn) & (self.df_errs['Msg_String'] == 'Base')
            base_row = self.df_errs[fil]

            # If rows found, set base code to first row's code
            if not base_row.empty:
                self.iCodeBase = base_row['iCode'].iloc[0]

    def SetReportErrCode(self):
        """
        Sets the report error code as the sum of base and local error codes.
        JDL 1/2/24
        """
        # If iCodeBase is not iErrNotFound, calculate .iCodeReport as sum of .iCodeBase and .iCodeLocal
        if self.iCodeBase != iErrNotFound:
            self.iCodeReport = self.iCodeBase + self.iCodeLocal