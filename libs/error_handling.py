#Version 2/14/24 Add IsLog option and logging functions
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

#Global code to flag Base error code not found in .df_errs
iErrNotFound = 10000

class ErrorHandle:
    def __init__(self, libs_dir, ErrMsgHeader='', IsHandle=True, IsPrint=True, IsLog=False):

        self.IsHandle = IsHandle

        self.Locn = ''  # Function where error occurred
        self.iCodeLocal = 0 # Local, integer error code
        self.iCodeBase = 0  # Base error code for .Locn lookup
        self.iCodeReport = 0 # Lookup code for error message (Base + Local)
        self.ErrParam = None # Optional param to append to error message
        self.ErrHeader = ErrMsgHeader # Error message header string
        self.ErrMsg = '' # Error message string
        self.IsNewErr = True # Flag for new error
        self.IsErr = False # Flag if error occurred

        #Import error codes from Excel file
        self.df_errs = pd.read_excel(libs_dir + 'ErrorCodes.xlsx', sheet_name='Errors_')

        self.IsWarning = False  # Flag for warning (non-fatal error)
        self.IsPrint = IsPrint  # Flag printing from ReportError
        self.IsLog = IsLog # Flag logging from ReportError
        self.Msgs_Accum = ''  # String with accumulated error messages
        
    """
    ================================================================================
    RecordErr Procedure - record/report an error or warning
    ================================================================================
    """
    def RecordErr(self):
        """
        Procedure to record/report an error or warning
        JDL 1/2/24
        """
        self.GetBaseErrCode()
        self.SetReportErrCode()
        #xxx
        #print('\nBase:', self.iCodeBase, self.iCodeLocal, self.iCodeReport)

        self.AppendErrMsg()
        self.ReportError()
        if self.IsWarning: self.ResetWarning()

    def GetBaseErrCode(self):
        """
        Look up Base .df_errs code for .Locn
        JDL 1/2/24
        """
        self.iCodeBase = iErrNotFound

        # Exit if self.Locn not  .df_errs Locn column values
        if self.Locn not in self.df_errs['Locn'].values: return

        # Find the Base row for self.Locn
        fil = (self.df_errs['Locn'] == self.Locn) & (self.df_errs['Msg_String'] == 'Base')
        base_row = self.df_errs.loc[fil]

        # Assign .iCodeBase to iCode from Locn + Msg_String match row
        if not base_row.empty: self.iCodeBase = base_row['iCode'].values[0]

    def SetReportErrCode(self):
        """
        Sets the report error code as the sum of base and local error codes
        JDL 1/2/24
        """
        # If no iCodeBase, leave iCodeReport as default value of 0
        if self.iCodeBase != iErrNotFound:
            self.iCodeReport = self.iCodeBase + self.iCodeLocal

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
        if self.ErrParam is not None: self.ErrMsg = self.ErrMsg + ': ' + self.ErrParam

    def ReportError(self):
        """
        Reports an error based on the ErrMsg attribute
        JDL 1/2/24
        """
        # Exit if .ErrMsg is empty
        if self.ErrMsg == '': return

        # Append .ErrMsg to .ErrMsgsAccum
        if self.Msgs_Accum: self.Msgs_Accum += '\n'
        self.Msgs_Accum += self.ErrMsg

        # Print the error message 
        if self.IsPrint:
            if (len(self.ErrHeader)>0) & (not self.IsWarning): 
                print(self.ErrHeader)
                if self.IsLog: logger.error(self.ErrHeader)
            print(self.ErrMsg)
            if self.IsLog: logger.error(self.ErrMsg)

    def ResetWarning(self):
        """
        Reset attributes to default values after reporting non-fatal/warning
        JDL 1/3/24
        """
        self.iCodeLocal = 0
        self.iCodeBase = 0
        self.iCodeReport = 0
        self.ErrMsg = ''
        self.ErrParam = None
        self.IsErr = False
    """
    =========================================================================
    ErrorHandle utility functions
    =========================================================================
    """
    def is_fail(self, is_error, i_code, Locn=None, err_param=None):
        """
        Boolean check condition; return True and  set class params if fail
        JDL 1/2/24; updated 1/11/24 to add Locn argument; 2/2/24 optional Locn
        """
        #Check boolean condition specified from calling function
        if not is_error: return False

        #If fail, set class parameters

        if not Locn is None: self.Locn = Locn
        self.IsErr = True
        self.iCodeLocal = i_code
        if err_param is not None: self.ErrParam = err_param
        return True

    def reset_log_file(self, logger_root):
        """
        Delete and reinitialize the log file
        """
        path_file = logger_root.handlers[0].baseFilename

        self.delete_log_file(logger_root, path_file)
        self.reinitialize_log_file(logger_root, path_file)
        
    def logger_filename(self, logger_root):
        """
        Return the name of the current logging file (when self.IsLog = True)
        """
        return logger_root.handlers[0].baseFilename

    def delete_log_file(self, logger, path_file):
        """
        Delete the current logging file
        """
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):

                handler.close()
                logger.removeHandler(handler)
                if os.path.isfile(path_file): os.remove(path_file)
                return path_file

    def reinitialize_log_file(self, logger, path_file):
        """
        Re-initialize the log file after deleting it
        """
        handler = logging.FileHandler(path_file)
        logger.addHandler(handler)