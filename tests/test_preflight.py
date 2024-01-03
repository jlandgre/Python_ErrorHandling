#Version 1/3/24
#python -m pytest test_preflight.py -v -s
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import sys, os
import pandas as pd
from io import StringIO
import pytest

# Import the class to be tested and mockup driver class
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.dirname(current_dir) +  os.sep + 'libs' + os.sep
if not libs_dir in sys.path: sys.path.append(libs_dir)
import preflight
from preflight import CheckExcelFiles
from error_handling import ErrorHandle
"""
=========================================================================
Fixtures and global variables for testing
=========================================================================
"""
@pytest.fixture
def errs():
    ErrHeader = 'The program encountered the following fatal error:'
    return ErrorHandle(libs_dir, ErrHeader, IsHandle=True)

@pytest.fixture
def df_errs_test():
    data = """
    iCode,Class,Locn,Msg_String
    100,CheckExcelFiles,ExcelFileExists,Base
    101,CheckExcelFiles,ExcelFileExists,ERROR: Input file not found
    """
    return pd.read_csv(StringIO(data), skipinitialspace=True)

"""
=========================================================================
Tests of CheckExcelFile class methods
=========================================================================
"""
def test_ExcelFileExists1(errs, df_errs_test):
    """
    Check if each Excel file exists and can be opened
    JDL 1/3/24
    """
    errs.df_errs = df_errs_test

    # instance CheckExcelFiles and check for file presence
    lst_files = ['../tests/test_mockup.xlsx']
    lst_shts = [['']]
    check_files = CheckExcelFiles(lst_files, lst_shts, errs)
    check_files.ExcelFileExists(errs)

    # Check that no error was recorded
    assert check_files.errs.IsErr == False

def test_ExcelFileExists2(errs, df_errs_test, capfd):
    """
    Check for file that does not exist
    JDL 1/3/24
    """
    errs.df_errs = df_errs_test

    # instance CheckExcelFiles and check for file presence
    lst_files = ['xxx.xlsx']
    lst_shts = [['']]
    check_files = CheckExcelFiles(lst_files, lst_shts, errs)
    check_files.ExcelFileExists(errs)

    # Capture the output
    out, err = capfd.readouterr()

    # Get the expected error message for iCode 101
    expected_msg = '\n\n ERROR: Input file not found: xxx.xlsx\n\n' 
    assert expected_msg == out

def test_SplitPath():
    path, f = preflight.SplitPath('../tests/test_mockup.xlsx')

    # Check that the directory path and file name are correct
    assert path == '../tests'
    assert f == 'test_mockup.xlsx'