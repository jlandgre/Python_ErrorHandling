#Version 1/2/24
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
Fixtures for testing
=========================================================================
"""
@pytest.fixture
def errs():
    return ErrorHandle(libs_dir, IsHandle=True)

@pytest.fixture
def df_errs_test():
    data = """
    iCode,Class,Locn,Msg_String
    100,DemoClass,check1,Base
    101,DemoClass,check1,A check1 error occurred
    105,DemoClass,check_no_base,No base row for Locn
    """
    return pd.read_csv(StringIO(data), skipinitialspace=True)

@pytest.fixture
def demo():
    return DemoClass()

"""
=========================================================================
=========================================================================
"""
def test_AppendErrMsg1(errs, df_errs_test):
    """
    Error message for case where iCodeReport is found
    """
    # Lookup iCodeBase and set iCodeReport and append the error message
    errs.df_errs = df_errs_test
    errs.Locn = 'check1'
    errs.iCodeLocal = 1
    errs.SetErrCodes()
    errs.AppendErrMsg()
    assert errs.ErrMsg == 'A check1 error occurred'

    # With pre-existing error message
    errs.ErrMsg = 'Pre-existing'
    errs.AppendErrMsg()
    assert errs.ErrMsg == 'Pre-existing\nA check1 error occurred'


def test_AppendErrMsg2(errs, df_errs_test):
    """
    Error message for case where iCodeBase not found
    """
    # Attempt to lookup iCodeBase and append the error message
    errs.df_errs = df_errs_test    
    errs.Locn = 'check_no_base'
    errs.iCodeLocal = 1
    errs.SetErrCodes()
    errs.AppendErrMsg()
    assert errs.ErrMsg == 'Base error code not found for function: check_no_base'

def test_AppendErrMsg3(errs, df_errs_test):
    """
    Error message for case where iCodeReport not found (But iCodeBase is found)
    """
    # Lookup iCodeBase and set iCodeReport
    errs.df_errs = df_errs_test
    errs.Locn = 'check1'
    errs.iCodeLocal = 2
    errs.SetErrCodes()

    # Attempt to look up iCodeReport (doesn't exist in df_errs))
    errs.AppendErrMsg()
    assert errs.ErrMsg == 'Error code not found for check1: 102'

def test_SetErrCodes(errs, df_errs_test):
    """
    Test SetErrCodes method
    """
    #Example  where Base row found
    errs.Locn = 'check1'
    errs.iCodeLocal = 1
    errs.df_errs = df_errs_test
    assert errs.SetErrCodes() == True
    assert errs.iCodeBase == 100
    assert errs.iCodeReport == 101

    #Example where Base row not found
    errs.iCodeBase = 0
    errs.Locn = 'check_no_base'
    assert errs.SetErrCodes() == False
    assert errs.iCodeBase == 10000
    
def test_errs_fixture(errs):
    """
    Check instancing of ErrorHandle class for testing
    JDL 1/2/24
    """
    assert errs is not None, "ErrorHandle instance should not be None"
    assert errs.df_errs.index.size > 0, "ErrorHandle.df_errs should have rows"

def test_is_fail(errs):
    """
    Boolean function to check fail/pass condition (evals True if fail)
    Set class parameters if fail
    JDL 1/2/24
    """
    result = errs.is_fail(True, 1, "test_param")
    assert result == True, "is_fail should return True when is_error is True"
    assert errs.iCodeLocal == 1, "iCodeLocal should be set to 1"
    assert errs.ErrParam == "test_param", "ErrParam should be set to 'test_param'"

    #Reinitialize errs and test with is_error = False
    errs = ErrorHandle(libs_dir, IsHandle=True)
    result = errs.is_fail(False, 1)
    assert result == False, "is_fail should return False when is_error is False"
    assert errs.iCodeLocal == 0, "iCodeLocal should be as initialized"
    assert errs.ErrParam == None, "ErrParam not specified"

