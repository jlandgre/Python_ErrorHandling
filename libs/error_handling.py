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
        #self.IsUserFacing = False
        self.IsNewErr = True
        #self.IsDriver = False
        self.IsErr = False
        self.df_errs = pd.read_excel(libs_dir + 'ErrorCodes.xlsx', sheet_name='Errors_')

    def is_fail(self, is_error, i_code, err_param=None):
        """
        Boolean function to check fail/pass condition (evals True if fail)
        Set class parameters if fail
        JDL 1/2/24
        """
        if not is_error: return False

        self.IsErr = True
        self.iCodeLocal = i_code
        if err_param is not None: self.ErrParam = err_param
        return True
    
    def SetErrCodes(self):
        """
        Look up Base df_errs code for .Locn and set iCodeReport
        JDL 1/2/24
        """
        self.iCodeBase = iErrNotFound

        # Check if self.Locn rows are found in the dataframe
        if self.Locn not in self.df_errs['Locn'].values: return False

        # Find the Base row for self.Locn
        fil = (self.df_errs['Locn'] == self.Locn) & (self.df_errs['Msg_String'] == 'Base')
        base_row = self.df_errs.loc[fil]

        # Assign self.iCodeBase to iCode from that row
        if not base_row.empty:
            self.iCodeBase = base_row['iCode'].values[0]
            self.iCodeReport = self.iCodeBase + self.iCodeLocal
            return True
        return False

    def AppendErrMsg(self):
        """
        Append error message for iCodeReport
        JDL 1/2/24
        """
        if not self.IsNewErr: return

        # Lookup error message for iCodeReport or set error message
        if self.iCodeBase == iErrNotFound:
            msgNew = "Base error code not found for function: " + self.Locn
        else:
            fil = self.df_errs['iCode'] == self.iCodeReport
            err_row = self.df_errs.loc[fil]
            if not err_row.empty:
                msgNew = err_row['Msg_String'].values[0]
            else:
                msgNew = 'Error code not found for ' + self.Locn +\
                            ': ' + str(self.iCodeReport)

        # Initialize .ErrMsg if empty then append new message
        if len(self.ErrMsg) > 0: self.ErrMsg = self.ErrMsg + '\n'
        self.ErrMsg = self.ErrMsg + msgNew

        # Append ErrParam if specified when ReportErr called
        if self.ErrParam is not None: self.ErrMsg = self.ErrMsg + ': ' & self.ErrParam

    def RecordErr(self):
    
        #Log error location; lookup base code and get iCodeReport for message lookup
        if self.IsNewErr:
            if self.GetBaseErrCode():
                self.iCodeReport = self.iCodeBase + self.iCodeLocal
