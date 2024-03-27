#Version 1/3/24
#python -m pytest test_preflight.py -v -s
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import sys, os
import pandas as pd
import numpy as np
from io import StringIO
import pytest
import logging

#Allow printing with logging.debug('xxx') commands
logging.basicConfig(level=logging.DEBUG)


# Import the class to be tested and mockup driver class
current_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.dirname(current_dir) +  os.sep + 'libs' + os.sep

if not libs_dir in sys.path: sys.path.append(libs_dir)
import preflight
from preflight import CheckExcelFiles
from error_handling import ErrorHandle
from preflight import CheckDataFrame
"""
=========================================================================
Fixtures and global variables for testing
=========================================================================
"""
@pytest.fixture
def errs():
    return ErrorHandle(libs_dir, '', IsHandle=True)

@pytest.fixture
def df_errs_test():
    """
    Use Excel file for testing error codes
    JDL 2/8/24
    """
    return pd.read_excel(libs_dir + 'ErrorCodes.xlsx', sheet_name='Errors_')


"""
=========================================================================
Tests of CheckDataFrame class methods
=========================================================================
"""

@pytest.fixture
def check_files(errs, df_errs_test):
    errs.df_errs = df_errs_test
    errs.Locn = 'CheckFilesProcedure'
    lst_files, lst_shts = ['../tests/test_mockup.xlsx'], [['']]
    return CheckExcelFiles(lst_files, lst_shts, errs)

@pytest.fixture
def df_test1():
    data = """
    Row_Name,Select,id_index,Color
    first_row,,1001,green
    second_row,x,1002,blue
    third_row,,1003,green
    fourth_row,x,1004,pink
    """
    df = pd.read_csv(StringIO(data.strip()), skipinitialspace=True)

    #Convert id_index to numeric and set as index
    df['id_index'] = df['id_index'].astype(int)
    df.set_index('Row_Name', inplace=True)
    return df

@pytest.fixture
def df_test2():
    data = """
    id_string,1002,1003,1004
    1002,0.02,0.03,0.04
    1003,0.05,0.06,0.07
    1004,0.08,0.09,0.1
    """
    df = pd.read_csv(StringIO(data.strip()), skipinitialspace=True)
    
    #Convert to numeric column names and id_string values
    df.rename(columns={col: int(col) for col in df.columns[1:]}, inplace=True)
    df['id_string'] = df['id_string'].astype(int)

    #Convert 1002 to 1004 column values to float
    for col in df.columns[1:]:
        df[col] = df[col].astype(float)

    df['id_string'] = df['id_string'].astype(int)
    df.set_index('id_string', inplace=True)
    return df

@pytest.fixture
def check_df1(errs, df_errs_test, df_test1):
    """
    Instance CheckDataFrame class with df_test1; use df_errs_test as error codes
    """
    errs.df_errs = df_errs_test
    return CheckDataFrame(df_test1, errs)

@pytest.fixture
def check_df2(errs, df_errs_test, df_test2):
    """
    Instance CheckDataFrame class with df_test2; use df_errs_test as error codes
    """
    errs.df_errs = df_errs_test
    return CheckDataFrame(df_test2, errs)


def test_CheckDataFrame_NoDuplicateCols(check_df2, capfd):
    """
    Check if the DataFrame self.df does not have duplicate column names
    JDL 1/11/24
    """
    # Test a case where there are no duplicate columns
    assert check_df2.NoDuplicateCols() == True

    # Modify check_df2.df to replace column 1004 with 1003 to create a duplicate
    check_df2.df.rename(columns={1004: 1003}, inplace=True)


    # Reset errs to initialized condition and Test a case where there are duplicate columns
    check_df2.errs.ResetWarning()
    assert check_df2.NoDuplicateCols() == False
    exp = 'ERROR: DataFrame cannot have duplicate columns and names cannot end in ".x" where x is a digit: \nDuplicate columns: 1003\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColumnsContainListVals(check_df2, capfd):
    """
    Check if the DataFrame columns contain a specified list of values
    JDL 1/11/24
    """
    # Test a list of values that are all in the columns
    assert check_df2.ColumnsContainListVals([1002, 1003]) == True

    # Reset errs to initialized condition and Test a list of values that are not all in the columns
    check_df2.errs.ResetWarning()
    assert check_df2.ColumnsContainListVals([1002, 1003, 1005]) == False
    exp = 'ERROR: DataFrame Columns must contain all specified values: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_IndexContainsListVals(check_df2, capfd):
    """
    Check if the DataFrame index contains a specified list of values
    JDL 1/11/24
    """
    # Test a list of values that are all in the index
    assert check_df2.IndexContainsListVals([1002, 1003]) == True

    # Reset errs to initialized condition and test list of values that are not all in the index
    check_df2.errs.ResetWarning()
    assert check_df2.IndexContainsListVals([1002, 1003, 1005]) == False
    exp = 'ERROR: Index must contain all specified values: \nMissing: 1005\n'
    check_printout(exp, capfd)
    
def test_CheckDataFrame_ColAllPopulated(check_df1, capfd):
    """
    Check if all values in a specified column are non-null
    JDL 1/11/24
    """
    # Test a column that contains only non-null values
    assert check_df1.ColAllPopulated('id_index') == True

    # Reset errs to initialized condition and Change a value to NaN
    check_df1.errs.ResetWarning()

    # Test the Select column which contains blanks
    assert check_df1.ColAllPopulated('Select') == False
    exp = 'ERROR: All column values must be non-blank: Select\n'
    check_printout(exp, capfd)
    

def test_CheckDataFrame_ColAllNumeric(check_df1, capfd):
    """
    Check if values in a specified column are non-blank and numeric
    JDL 1/11/24
    """

    # Test a column that contains only numeric values
    assert check_df1.ColAllNumeric('id_index') == True

    # Reset errs to initialized condition and Change a value to a string
    check_df1.errs.ResetWarning()
    check_df1.df.loc['first_row', 'id_index'] = 'xyz'

    # Test the column again
    assert check_df1.ColAllNumeric('id_index') == False
    exp = 'ERROR: Column must contain only non-blank numeric values: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ContainsRequiredCols(check_df1, capfd):
    """
    Check if .df contains a specified list of column names
    JDL 1/11/24
    """
    # Test a list of columns that are in the DataFrame
    lst = list(check_df1.df.columns)
    assert check_df1.ContainsRequiredCols(lst) == True

    # Reset errs to initialized condition
    check_df1.errs.ResetWarning()

    # Test a list of columns where at least one is not in the DataFrame
    lst = lst + ['non_existent_column']
    assert check_df1.ContainsRequiredCols(lst) == False
    exp = 'ERROR: Required column not present: non_existent_column\n'
    check_printout(exp, capfd)

    
def test_CheckDataFrame_ColNonBlank(check_df1):
    """
    Test that ColNonBlank checks if a specified column contains any non-blank values
    JDL 1/11/24
    """
    # Test a column that contains non-blank values
    assert check_df1.ColNonBlank('Select') == True

    # Reset errs to initialized condition
    check_df1.errs.ResetWarning()

    # Test a column that contains only blank values and check error message printout
    check_df1.df['Select_blank'] = np.nan
    assert check_df1.ColNonBlank('Select_blank') == False
    exp = 'ERROR: Required column is blank: Select_blank\n'
    #check_printout(exp, capfd)

def check_printout(expected, capfd):
    """
    Check that the printed output matches the expected output
    JDL 1/11/24
    """
    captured = capfd.readouterr()
    #if captured.out != expected:
    #    logging.debug("\ncaptured.out\n")
    #    logging.debug(captured.out)
    #    logging.debug('\n\nexpected\n')
    #    logging.debug(expected)

    assert captured.out == expected
    
def test_CheckDataFrame_instance(check_df1):
    """
    Test that CheckDataFrame properly instances the class
    JDL 1/11/24
    """
    # Check that check_df is an instance of CheckDataFrame
    assert isinstance(check_df1, preflight.CheckDataFrame)

    # Check that the DataFrame and ErrorHandle instance are correctly set as attributes
    assert isinstance(check_df1.df, pd.DataFrame)
    assert isinstance(check_df1.errs, ErrorHandle)

def test_df_test1(df_test1):
    """
    Check that df_test1 fixture was instanced as intended
    JDL 1/11/24
    """
    # Check the shape of the DataFrame
    assert df_test1.shape == (4, 3)

    # Check the column names
    assert list(df_test1.columns) == ['Select', 'id_index', 'Color']

    # Check the data type of the 'id_index' column
    assert df_test1['id_index'].dtypes == 'int64'

    # Check some values in the DataFrame
    rows = ['second_row', 'third_row', 'fourth_row']
    cols = ['Select', 'id_index', 'Color']
    vals = ['x', 1003, 'pink']
    for (row, col, val) in zip(rows, cols, vals):
        assert df_test1.loc[row, col] == val

def test_df_test2(df_test2):
    """
    Check that df_test2 fixture was instanced as intended
    """
    # Check the shape of the DataFrame
    assert df_test2.shape == (3, 3)

    # Check the column names
    assert list(df_test2.columns) == [1002, 1003, 1004]

    # Check the name and data type of the index
    assert df_test2.index.name == 'id_string'
    assert df_test2.index.dtype == 'int64'

    # Check the data type of the other columns
    for col in df_test2.columns:
        assert df_test2[col].dtypes == 'float64'

    # Check some values in the DataFrame
    for idx, val in zip([1002, 1003, 1004], [0.02, 0.06, 0.10]):
        assert df_test2.loc[idx, idx] == val

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

IsPrint = False

def test_CheckFilesProcedure1(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (1) Check of case where there are no errors
    """
    check_files.lst_shts = [['first_sheet', 'second_sheet']]
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

    if IsPrint & (not check_files.IsWbErr): print('\n\nNo errors\n')

def test_CheckFilesProcedure2(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class 
    (2) non-existent file
    """
    check_files.lst_files = ['xxxx.xlsx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not found'

    if IsPrint: print_msgs_accum(check_files)

def test_CheckFilesProcedure3(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (3) non-Excel file
    """
    check_files.lst_files = ['../tests/dummy_file.docx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not a val'

    if IsPrint: print_msgs_accum(check_files)

def test_CheckFilesProcedure4(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (4) non-existent sheet
    """
    check_files.lst_shts = [['first_sheet', 'x_sheet', 'second_sheet']]
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:32] == 'ERROR: Required input file sheet'

    if IsPrint: print_msgs_accum(check_files)

def print_msgs_accum(check_files):
    """Print accumulated error messages"""
    print('\n\n', check_files.errs.Msgs_Accum + '\n')

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