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
    100,CheckExcelFiles,CheckFilesProcedure,Base
    101,CheckExcelFiles,CheckFilesProcedure,ERROR: Input file not found
    102,CheckExcelFiles,CheckFilesProcedure,ERROR: Input file not a valid Excel file
    103,CheckExcelFiles,CheckFilesProcedure,ERROR: Required input file sheet not found
    """
    return pd.read_csv(StringIO(data), skipinitialspace=True)

@pytest.fixture
def check_files(errs, df_errs_test):
    errs.df_errs = df_errs_test
    errs.Locn = 'CheckFilesProcedure'
    lst_files, lst_shts = ['../tests/test_mockup.xlsx'], [['']]
    return CheckExcelFiles(lst_files, lst_shts, errs)
"""
=========================================================================
Tests of CheckExcelFiles.CheckFilesProcedure() methods

These tests use the mockup Excel file, test_mockup.xlsx and a dummy
non-Excel file, dummy_file.docx in the tests directory. The tests use
a virtual import of df_errs_test to construct the error code df that
would typically be imported from ErrorCodes.xlsx. It would reside in
the libs subfolder with error_handling.py and preflight.py files.
=========================================================================
"""
def test_CheckFilesProcedure1(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (1) Check of case where there are no errors
    """
    check_files.lst_shts = [['first_sheet', 'second_sheet']]
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

def test_CheckFilesProcedure2(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class 
    (2) non-existent file
    """
    check_files.lst_files = ['xxxx.xlsx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not found'


def test_CheckFilesProcedure3(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (3) non-Excel file
    """
    check_files.lst_files = ['../tests/dummy_file.docx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not a val'

def test_CheckFilesProcedure4(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (4) non-existent sheet
    """
    check_files.lst_shts = [['first_sheet', 'x_sheet', 'second_sheet']]
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:32] == 'ERROR: Required input file sheet'

    # Print accumulated error messages
    #msgs = check_files.errs.Msgs_Accum
    #if len(msgs) > 0: print('\n\n', msgs + '\n')

def test_ExcelFileExists1(check_files):
    """
    Check if each Excel file exists and can be opened
    JDL 1/3/24
    """

    # instance CheckExcelFiles and check for file presence
    check_files.ExcelFileExists(idx=0)

    # Check that no error was recorded
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

def test_ExcelFileExists2(check_files):
    """
    Check for file that does not exist
    JDL 1/3/24
    """
    # instance CheckExcelFiles and check for file presence
    check_files.lst_files = ['xxx.xlsx']
    check_files.ExcelFileExists(idx=0)

    # Get the expected error message for iCode 101
    expected_msg = 'ERROR: Input file not found: \n '\
                    + check_files.lst_files[0] + '\n'
    assert check_files.errs.Msgs_Accum == expected_msg

def test_ExcelFileOpens1(check_files):
    """
    Check if Excel file opens successfully
    JDL 1/4/24
    """
    # Check file opens for valid Excel file
    check_files.ExcelFileOpens(idx=0)
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

def test_ExcelFileOpens2(check_files):
    """
    Check attempt to open non-Excel file
    JDL 1/4/24
    """
    # check non-Excel test file
    check_files.lst_files = ['../tests/dummy_file.docx']
    check_files.ExcelFileOpens(idx=0)

    assert check_files.IsWbErr == True
    expected_msg = 'ERROR: Input file not a valid Excel file: \n '\
    + check_files.lst_files[0] + '\n' 
    assert check_files.errs.Msgs_Accum == expected_msg

def test_AllSheetsExist1(check_files):
    """
    Test if all specified sheets exist in the Excel workbook
    JDL 1/4/24
    """

    # Set the wb object by running check that file opens
    idx = 0
    check_files.ExcelFileOpens(idx)
    check_files.lst_shts = [['first_sheet', 'second_sheet']]

    check_files.AllSheetsExist(idx)
    assert check_files.IsWbErr == False

def test_AllSheetsExist2(check_files):
    """
    Test that non-existent sheet triggers error
    """
    idx = 0
    check_files.ExcelFileOpens(idx)
    check_files.lst_shts = [['first_sheet', 'x_sheet', 'second_sheet']]
    check_files.AllSheetsExist(idx)

    assert check_files.IsWbErr == True
    expected_msg ='ERROR: Required input file sheet not found: \n '\
                    'Missing: x_sheet in ' + check_files.lst_files[idx] + '\n'
    assert check_files.errs.Msgs_Accum == expected_msg

def test_SheetExists(check_files):
    """
    Check if specified sheet exists in Excel workbook
    JDL 1/4/24
    """
    # Set the wb object by running FileOpens check
    idx = 0
    check_files.ExcelFileOpens(idx)

    # Two sheets that exist 
    assert check_files.SheetExists(idx, 'first_sheet') == True
    assert check_files.SheetExists(idx, 'second_sheet') == True
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

    # One sheet that does not exist
    assert check_files.SheetExists(idx, 'third_sheet') == False
    assert check_files.IsWbErr == True
    expected_msg ='ERROR: Required input file sheet not found: \n '\
                    'Missing: third_sheet in ' + check_files.lst_files[0] + '\n'
    assert check_files.errs.Msgs_Accum == expected_msg