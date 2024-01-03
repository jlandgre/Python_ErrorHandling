#Version 1/3/24
#python -m pytest test_error_handling.py -v -s
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import sys, os
import pandas as pd
from io import StringIO
import pytest

# Import the class to be tested and mockup driver class
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.dirname(current_dir) +  os.sep + 'libs' + os.sep
if not libs_dir in sys.path: sys.path.append(libs_dir)
from error_handling import ErrorHandle
from demo import DemoClass

"""
=========================================================================
Fixtures and global variables for testing
=========================================================================
"""
iErrNotFound = 10000

@pytest.fixture
def errs():
    ErrHeader = 'The program encountered the following fatal error:'
    return ErrorHandle(libs_dir, ErrHeader, IsHandle=True)

@pytest.fixture
def df_errs_test():
    data = """
    iCode,Class,Locn,Msg_String
    100,DemoClass,check1,Base
    101,DemoClass,check1,A check1 error occurred
    105,DemoClass,check_no_base,No base row for Locn
    110,DemoClass,check3,Base
    111,DemoClass,check3,Warning: check3
    """
    return pd.read_csv(StringIO(data), skipinitialspace=True)

@pytest.fixture
def demo():
    return DemoClass()

"""
=========================================================================
Tests of ErrorHandle class methods
=========================================================================
"""
def test_ResetWarning(errs, df_errs_test, capfd):
    """
    Reset attributes to default values after reporting non-fatal/warning
    JDL 1/2/24
    """
    # Call the helper function with for a warning message
    errs.IsWarning = True
    errs = InitErrsForTestAppendErrMsg(errs, df_errs_test, 'check3', 1)
    errs.ReportError()

    # Check that ReportError prints the error message
    print_output_expected = 'Warning: check3\n'
    assert capfd.readouterr()[0] == print_output_expected

    if errs.IsWarning: errs.ResetWarning()
    for att, expected in zip([errs.iCodeLocal, errs.iCodeBase, \
                errs.iCodeReport, errs.ErrMsg], [0, 0, 0, '']):
        assert att == expected

def test_ReportError(errs, df_errs_test, capfd):
    """
    Reports an error based on the ErrMsg attribute.
    JDL 1/2/24
    """
    # Call the helper function with Locn='check1' and iCodeLocal=1
    errs = InitErrsForTestAppendErrMsg(errs, df_errs_test, 'check1', 1)
    errs.ReportError()

    # Check that ReportError prints the error message
    s = 'The program encountered the following fatal error:\nA check1 error occurred\n'
    print_output_expected = s
    assert capfd.readouterr()[0] == print_output_expected

    # Check that .ErrMsg is appended to .ErrMsgsAccum
    assert errs.Msgs_Accum == 'A check1 error occurred'

def test_AppendErrMsg1(errs, df_errs_test):
    """
    Error message for case where iCodeReport is found
    JDL 1/2/24
    """
    # Lookup iCodeBase and set iCodeReport and append the error message
    errs = InitErrsForTestAppendErrMsg(errs, df_errs_test, 'check1', 1)
    assert errs.ErrMsg == 'A check1 error occurred'

    # With pre-existing error message
    errs.ErrMsg = 'Pre-existing'
    errs.AppendErrMsg()
    assert errs.ErrMsg == 'Pre-existing\nA check1 error occurred'

def test_AppendErrMsg2(errs, df_errs_test):
    """
    Error message for case where iCodeBase not found
    JDL 1/2/24
    """
    # Attempt to lookup iCodeBase and append the error message
    errs = InitErrsForTestAppendErrMsg(errs, df_errs_test, 'check_no_base', 1)
    assert errs.ErrMsg == 'Base error code not found for function: check_no_base'

def test_AppendErrMsg3(errs, df_errs_test):
    """
    Error message for case where iCodeReport not found (But iCodeBase is found)
    JDL 1/2/24
    """
    # Attempt to look up iCodeReport (doesn't exist in df_errs))
    errs = InitErrsForTestAppendErrMsg(errs, df_errs_test, 'check1', 2)
    assert errs.ErrMsg == 'Error code not found for check1: 102'

def InitErrsForTestAppendErrMsg(errs, df_errs_test, Locn, iCodeLocal):
    """
    Helper function for initializing testing of AppendErrMsg
    JDL 1/2/24
    """
    errs.df_errs = df_errs_test
    errs.Locn = Locn
    errs.iCodeLocal = iCodeLocal
    errs.GetBaseErrCode()
    errs.SetReportErrCode()
    errs.AppendErrMsg()
    return errs

def test_SetReportErrCode(errs, df_errs_test):
    """
    Sets the report error code as the sum of base and local error codes.
    JDL 1/2/24
    """
    # Set the error dataframe in the ErrorHandle instance
    errs.df_errs = df_errs_test

    # Case 1: Base and Report error codes found in .df_errs 
    errs.Locn, errs.iCodeLocal = 'check1', 1
    errs.GetBaseErrCode()
    errs.SetReportErrCode()
    assert errs.iCodeReport == 101, 'Base error and Report error codes found in .df_errs'

    # Case 2: Base error code found in .df_errs but .iCodeLocal corresponds to a .iCodeReport value of 2 that is not found in .df_errs
    errs.iCodeReport = 0 # Reset to default
    errs.iCodeLocal = 2
    errs.GetBaseErrCode()
    errs.SetReportErrCode()
    assert errs.iCodeReport == 102, 'Base error code but missing iCodeReport'

    # Case 3: Base error code not found in .df_errs
    errs.iCodeReport = 0 # Reset to default
    errs.Locn, errs.iCodeLocal = 'check_no_base', 2
    errs.GetBaseErrCode()
    errs.SetReportErrCode()
    assert errs.iCodeReport == 0, 'Base error code not found in .df_errs'

def test_GetBaseErrCode(errs, df_errs_test):
    """
    Set base error code based on location.
    JDL 1/2/24
    """

    # Set the error dataframe in the ErrorHandle instance
    errs.df_errs = df_errs_test

    # Initialize .iCodeLocal to 1
    errs.iCodeLocal = 1

    # Test case where the Base row is found in .df_errs
    errs.Locn = 'check1'
    errs.GetBaseErrCode()
    assert errs.iCodeBase == 100, 'Base row found, but incorrect iCodeBase set'

    # Test case where the Base row is not found in .df_errs
    errs.Locn = 'check_no_base'
    errs.GetBaseErrCode()
    assert errs.iCodeBase == iErrNotFound, 'Base row not found, but iCodeBase not set to iErrNotFound'

def test_errs_fixture(errs):
    """
    Check instancing of ErrorHandle class for testing
    JDL 1/2/24
    """
    assert errs is not None
    assert errs.df_errs.index.size > 0

def test_is_fail(errs):
    """
    Boolean function to check fail/pass condition (evals True if fail)
    Set class parameters if fail
    JDL 1/2/24
    """
    result = errs.is_fail(True, 1, 'test_param')
    assert result == True, 'is_fail should return True when is_error is True'
    assert errs.iCodeLocal == 1, 'iCodeLocal should be set to 1'
    assert errs.ErrParam == 'test_param', 'ErrParam should be set to test_param'

    #Reinitialize errs and test with is_error = False
    errs = ErrorHandle(libs_dir, IsHandle=True)
    result = errs.is_fail(False, 1)
    assert result == False, 'is_fail should return False when is_error is False'
    assert errs.iCodeLocal == 0, 'iCodeLocal should be as initialized'
    assert errs.ErrParam == None, 'ErrParam not specified'