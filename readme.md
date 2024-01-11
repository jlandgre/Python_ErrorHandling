This project contains code libraries for user messaging and for performing prechecks on inputs for Python projects. 

error_handling.py and its ErrorHandle class manage reporting errors and warnings indexed by a local, integer code and a base error code for each function in a code project. A table of codes and corresponding message strings is stored in the ErrorCodes.xlsx file making it easy to add new messages or edit the existing ones. ErrorHandle is loosely based on this [VBA_ErrorHandling project](https://github.com/jlandgre/VBA_ErrorHandling) that has been used successfully in VBA consulting projects.

preflight.py uses the ErrorHandle class to precheck inputs for a project. The CheckExcelFiles class can check whether a user-specified list of files exists and contains a specified list of named sheets for each file.

The tests/test_error_handling.py and tests/test_preflight.py include examples of using error_handle and preflight code.

A key goal of this project is to make it possible for user messages to be a configuration (e.g. in ErrorCodes.xlsx) instead of needing to be hard coded. A related objective is to minimize extra code and clutter related to trapping and reporting errors. Another objective is to make it possible to trap errors in nested functions where it may be desirable to return up the chain from where the error was detected --allowing an orderly shutdown of in-progress proceedings before reporting the error to the user and halting execution.

This function from preflight.py gives an example of trapping an error if a specified file doesn't exist. Here, self.errs is an instance of the ErrorHandle class --passed to the function as an attribute of the preflight.CheckExcelFiles class. This code relies on ErrorHandle.Locn having already been set in a calling function to specify how to look up the appropriate message from ErrorCodes. The ErrorHandle.is_fail() function checks the specified, Boolean argument and sets a local code "1" and an optional string parameter to report
```
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
```

If an input file is mis-specified and the .is_fail check returns True,  ErrorHandle.RecordErr() method will report the following message and either halt execution or continue depending on the value of an ErrorHandle.IswWarning Boolean flag.
```
ERROR: Specified file not found: 
 path_tofile\filename.ext
```

J.D. Landgrebe, Data Delve LLC
January 2024