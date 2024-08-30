This project contains Python libraries for user messaging/error handling and for performing prechecks on Excel file and Pandas DataFrame inputs for Python projects. Such prechecks can prevent problems that would be mysterious to the user and difficult to troubleshoot. Demo.ipynb gives examples of different approaches to incorporating these modules into a project's code.

A design goal is to have user messages  be a configuration instead of hard coded. We do this from a table in an ErrorCodes.xlsx file where messages can be looked up by the name of the function where the error occurred and an integer index specific to the error check. This minimizes extra code and clutter related to trapping and reporting errors in functions. Another objective is to make it possible to trap errors in nested functions where it may be desirable to return up the chain from where the error was detected to perform additional steps before reporting the error. This enables an orderly shutdown of in-progress proceedings before reporting the error to the user and halting execution.

__error_handling.py (test_error_handling.py)__
error_handling.py and its ErrorHandle class manage reporting errors and warnings indexed by a local, integer code and a base error code for each function in a code project. A table of codes and corresponding message strings is stored in the ErrorCodes.xlsx file making it easy to add new messages or edit the existing ones. ErrorHandle is based on this [VBA_ErrorHandling project](https://github.com/jlandgre/VBA_ErrorHandling) that has been used successfully in VBA consulting projects.

__preflight.py (test_preflight.py)__
preflight.py uses the ErrorHandle class to precheck inputs for a project. The CheckExcelFiles class can check whether a user-specified list of files exists and contains a specified list of named sheets for each file. The CheckDataFrame class can perform the following preflight checks on an input DataFrame, df:
* df contains list of required columns
* df has no duplicate columns
* df has no duplicate indices
* list of columns is completely populated with non-blank values
* df columns include a specified list of values
* df index includes a specified list of values
* df column contains a specified list of values
* df column does not have duplicates of a specified list of values
* list of columns all contain at least one non-blank value
* list of columns contain all numeric values
* list of columns contain numeric values within a range specified by a lower and/or upper numeric limit
* df column values all match a specified Regex pattern
* df location's value matches a specified Regex pattern

The function below from preflight.py gives an example of trapping an error if a specified file at fpath doesn't exist. Here, self.errs is an instance of the ErrorHandle class --passed to the function as an attribute of the preflight.CheckExcelFiles class. This code relies on ErrorHandle.Locn having already been set in a calling function to specify how to look up the appropriate message from ErrorCodes. 
```
    def ExcelFileExists(self, idx):
        """
        Check if an Excel file exists based on specified list index for list 
        of files to check (iteration over list in calling CheckFilesProcedure)
        """
        fpath = self.lst_files[idx]

        if not os.path.exists(fpath):

            #Shorten the directory path for printing
            fpath = util.ck_for_shorten_path(self.lst_files[idx], 3)

            #Set errs params and report the error (add to self.errs.Msgs_Accum)
            self.errs.is_fail(True, 1, self.errs.Locn, '\n ' + fpath + '\n')
            self.IsWbErr = True
            self.errs.RecordErr()
            return False
        return True
```
The ErrorHandle.is_fail() function checks the specified, Boolean argument and sets a local code, 1, and an optional string parameter to report with the message listed in ErrorCodes.xlsx. The .RecordErr() method looks up a base error code for errs.Locn and adds the local, 1, code to the base to look up the message to report. This lookup approach means that the local error codes within the code can be simple integers --counting up from 1 rather than needing to be globally unique within the project. That makes administration easier.

The errs.Locn argument is a pre-specified location that is the lookup key for the message. If this were not pre-specified, errs.Locn can be replaced with "inspect.currentframe().f_code.co_name" to get the current function name.

Using .is_fail() minimizes code clutter to check for an error. In the example, there is a multiline "if block," but, if the error condition will be reported later at the top of a stack of nested functions, the check can be single line and simply return if an error is detected. In this case, the .is_fail() call can conditionally return to the calling function.

For the above example, if the .is_fail() Boolean check (first argument) returns True, the errs.RecordErr()  will report the following message and either halt execution or continue depending on the value of an errs.IswWarning Boolean flag.
```
ERROR: Specified file not found: 
path_tofile\filename.ext
```

J.D. Landgrebe, Data Delve LLC
January 2024; Updated February 19, 2024