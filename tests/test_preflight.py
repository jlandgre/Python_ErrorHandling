#Version 8/27/24
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
from preflight import CheckExcelFiles
from preflight import CheckDataFrame
from error_handling import ErrorHandle
from projtables import Table
"""
=========================================================================
Fixtures and global variables for testing
=========================================================================
"""
@pytest.fixture
def errs():
    return ErrorHandle(libs_dir, '', IsHandle=True)

@pytest.fixture
def path_err_codes():
    return libs_dir + 'ErrorCodes.xlsx'

@pytest.fixture
def df_errs_test(path_err_codes):
    """
    Use Excel file for testing error codes
    JDL 2/8/24
    """
    return pd.read_excel(path_err_codes, sheet_name='Errors_')

"""
=========================================================================
Tests of CheckDataFrame and CheckDataFrame class methods
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

    #Convert id_index column to numeric and set as index
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
def tbl():
    """
    Instance dummy Table class to use in testing CheckDataFrame
    JDL 8/26/24
    """
    return Table('', 'Dummy_Table', '', '')

@pytest.fixture
def checkdf1(df_test1, tbl):
    """
    Instance CheckDataFrame instance with df_test1
    """
    tbl.name, tbl.df = 'df_test1', df_test1
    return CheckDataFrame(libs_dir, tbl)

@pytest.fixture
def checkdf2(df_test2, tbl):
    """
    Instance CheckDataFrame instance with df_test2
    """
    tbl.name, tbl.df = 'df_test2', df_test2
    return CheckDataFrame(libs_dir, tbl)

"""
=========================================================================
Check fixture dataframes for validation
=========================================================================
"""
def test_fixtures_df_test1(df_test1):
    """
    df_test1 DataFrame fixture
    JDL 8/26/24
    """
    assert df_test1.shape == (4, 3)
    assert df_test1.columns.tolist() == ['Select', 'id_index', 'Color']
    assert df_test1.index.name == 'Row_Name'

    # Check the data type of the 'id_index' column
    assert df_test1['id_index'].dtypes == 'int64'

    # Check some values in the DataFrame
    rows = ['second_row', 'third_row', 'fourth_row']
    cols = ['Select', 'id_index', 'Color']
    vals = ['x', 1003, 'pink']
    for (row, col, val) in zip(rows, cols, vals):
        assert df_test1.loc[row, col] == val

def test_fixtures_df_test2(df_test2):
    """
    df_test2 DataFrame fixture
    JDL 8/26/24
    """
    assert df_test2.shape == (3, 3)
    assert df_test2.columns.tolist() == [1002, 1003, 1004]
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
"""
def test_CheckDataFrame_checkdf1(checkdf1):
    """
    check_df1 CheckDataFrame instance fixture with df_test1
    JDL 8/26/24
    """
    assert isinstance(checkdf1.tbl, Table)
    assert isinstance(checkdf1.errs, ErrorHandle)
    assert checkdf1.tbl.df.shape == (4, 3)

def test_CheckDataFrame_checkdf2(checkdf2):
    """
    check_df2 CheckDataFrame instance fixture with df_test2
    JDL 8/26/24
    """
    assert isinstance(checkdf2.tbl, Table)
    assert isinstance(checkdf2.errs, ErrorHandle)
    assert checkdf2.tbl.df.shape == (3, 3)
"""
=========================================================================
"""

def test_CheckExcelFiles_check_files(check_files):
    """
    check_files CheckExcelFiles instance fixture
    JDL 8/26/24
    """
    assert len(check_files.lst_files) == 1
    assert isinstance(check_files, CheckExcelFiles)
    assert isinstance(check_files.errs, ErrorHandle)


"""
=========================================================================
CheckDataFrame preflight tests
(Takes tbl / tbl.df as input for "1" tests; df for "2" tests)
=========================================================================
"""
def test_CheckDataFrame_ContainsRequiredCols1(checkdf1, capfd):
    """
    .tbl.df contains specified list of column names (True if so)
    JDL 1/11/24; Modified 8/27/24
    """
    # Test a list of columns that are in the DataFrame
    lst = list(checkdf1.tbl.df.columns)
    assert checkdf1.ContainsRequiredCols(lst) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test a list of columns where at least one is not in the DataFrame
    lst = lst + ['non_existent_column']
    assert checkdf1.ContainsRequiredCols(lst) == False
    exp = 'ERROR: Required column not present: non_existent_column\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ContainsRequiredCols2(checkdf1, capfd):
    """
    df contains specified list of column names (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ContainsRequiredCols'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a list of columns that are in the DataFrame
    lst = list(df_test.columns)
    assert checkdf1.ContainsRequiredCols(lst, df=df_test) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test a list of columns where at least one is not in the DataFrame
    lst = lst + ['non_existent_column']
    assert checkdf1.ContainsRequiredCols(lst, df=df_test) == False
    exp = 'custom_ContainsRequiredCols: non_existent_column\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateCols1(checkdf2, capfd):
    """
    .tbl.df has unique column names (True if so)
    JDL 1/11/24
    """
    # Test a case where there are no duplicate columns
    assert checkdf2.NoDuplicateCols() == True

    # Modify checkdf2.df to replace column 1004 with 1003 to create a duplicate
    checkdf2.tbl.df.rename(columns={1004: 1003}, inplace=True)

    # Reset errs to initialized condition and Test a case where there are duplicate columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.NoDuplicateCols() == False
    exp = 'ERROR: DataFrame cannot have duplicate columns and names cannot end in ".x" where x is a digit: \nDuplicate columns: 1003\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateCols2(checkdf2, capfd):
    """
    df has unique column names (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_NoDuplicateCols'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    # Test a case where there are no duplicate columns
    assert checkdf2.NoDuplicateCols(df=df_test) == True

    # Modify checkdf2.df to replace column 1004 with 1003 to create a duplicate
    df_test.rename(columns={1004: 1003}, inplace=True)

    # Reset errs to initialized condition and Test a case where there are duplicate columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.NoDuplicateCols(df=df_test) == False
    exp = 'custom_NoDuplicateCols: \nDuplicate columns: 1003\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateIndices1(checkdf2, capfd):
    """
    .tbl.df has unique index values (True if so)
    JDL 1/11/24
    """
    # Test a case where there are no duplicate indices
    assert checkdf2.NoDuplicateIndices() == True

    # Modify checkdf2.df to replace 1003 index to create a duplicate
    checkdf2.tbl.df.index = [1002, 1002, 1004]

    # Reset errs to initialized condition and Test a case where there are duplicate columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.NoDuplicateIndices() == False
    exp = 'ERROR: DataFrame index values must be unique: \nDuplicate indices: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateIndices2(checkdf2, capfd):
    """
    df has unique index values (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_NoDuplicateIndices'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    # Test a case where there are no duplicate indices
    assert checkdf2.NoDuplicateIndices(df=df_test) == True

    # Modify checkdf2.df to replace 1003 index to create a duplicate
    df_test.index = [1002, 1002, 1004]

    # Reset errs to initialized condition and Test a case where there are duplicate columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.NoDuplicateIndices(df=df_test) == False
    exp = 'custom_NoDuplicateIndices: \nDuplicate indices: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsPopulated1(checkdf1, capfd):
    """
    .tbl.df list of tbl.populated_cols populated with non-blank values (True if so)
    JDL 8/27/24
    """
    #Set tbl attribute list of columns that must be populated
    checkdf1.tbl.populated_cols = ['id_index', 'Color']

    #Test list with columns that are all populated
    assert checkdf1.LstColsPopulated() == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    #Set tbl attribute list of columns that must be populated
    checkdf1.tbl.populated_cols = ['Select', 'Color']

    # Test list with column that is not all populated
    assert checkdf1.LstColsPopulated() == False
    exp = 'ERROR: All column values must be non-null: Select\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsPopulated2(checkdf1, capfd):
    """
    .tbl.df list of tbl.populated_cols populated with non-blank values (True if so)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColPopulated'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    #Set list of columns that must be populated
    lst = ['id_index', 'Color']

    #Test list with columns that are all populated
    assert checkdf1.LstColsPopulated(df=df_test, lst_cols=lst) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    #Set tbl attribute list of columns that must be populated
    lst = ['Select', 'Color']

    # Test list with column that is not all populated
    assert checkdf1.LstColsPopulated(df=df_test, lst_cols=lst) == False
    exp = 'custom_ColPopulated: Select\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColPopulated1(checkdf1, capfd):
    """
    All values in a specified column are non-null (True if so)
    JDL 1/11/24
    """
    # Test a column that contains only non-null values
    assert checkdf1.ColPopulated('id_index') == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    # Test the Select column which contains blanks
    assert checkdf1.ColPopulated('Select') == False
    exp = 'ERROR: All column values must be non-null: Select\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColPopulated2(checkdf1, capfd):
    """
    All values in a specified column are non-null (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColPopulated'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column that contains only non-null values
    assert checkdf1.ColPopulated('id_index', df=df_test) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    # Test the Select column which contains blanks
    assert checkdf1.ColPopulated('Select', df=df_test) == False
    exp = 'custom_ColPopulated: Select\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColumnsContainListVals1(checkdf2, capfd):
    """
    DataFrame columns contain a specified list of values
    JDL 1/11/24
    """
    # Test a list of values that are all in the columns
    assert checkdf2.ColumnsContainListVals([1002, 1003]) == True

    # Reset errs to initialized condition and Test a list of values that are not all in the columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.ColumnsContainListVals([1002, 1003, 1005]) == False
    exp = 'ERROR: DataFrame Columns must contain all specified values: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColumnsContainListVals2(checkdf2, capfd):
    """
    DataFrame columns contain a specified list of values
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_ColumnsContainListVals'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    # Test a list of values that are all in the columns
    assert checkdf2.ColumnsContainListVals([1002, 1003], df=df_test) == True

    # Reset errs to initialized condition and Test a list of values that are not all in the columns
    checkdf2.errs.ResetWarning()
    assert checkdf2.ColumnsContainListVals([1002, 1003, 1005], df=df_test) == False
    exp = 'custom_ColumnsContainListVals: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_IndexContainsListVals1(checkdf2, capfd):
    """
    DataFrame index contains a specified list of values
    JDL 1/11/24
    """
    # Test a list of values that are all in the index
    assert checkdf2.IndexContainsListVals([1002, 1003]) == True

    # Reset errs to initialized condition and test list of values that are not all in the index
    checkdf2.errs.ResetWarning()
    assert checkdf2.IndexContainsListVals([1002, 1003, 1005]) == False
    exp = 'ERROR: Index must contain all specified values: \nMissing: 1005\n'
    check_printout(exp, capfd)
    
def test_CheckDataFrame_IndexContainsListVals2(checkdf2, capfd):
    """
    DataFrame index contains a specified list of values
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_IndexContainsListVals'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    # Test a list of values that are all in the index
    assert checkdf2.IndexContainsListVals([1002, 1003], df=df_test) == True

    # Reset errs to initialized condition and test list of values that are not all in the index
    checkdf2.errs.ResetWarning()
    assert checkdf2.IndexContainsListVals([1002, 1003, 1005], df=df_test) == False
    exp = 'custom_IndexContainsListVals: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllNonBlank1(checkdf1, capfd):
    """
    .tbl.df list of tbl.nonblank_cols all contain at least one non-blank value (True if so)
    JDL 8/27/24
    """
    #Set tbl attribute list of columns that must be populated
    checkdf1.tbl.nonblank_cols = ['id_index', 'Color']

    #Test list with columns that are all populated
    assert checkdf1.LstColsAllNonBlank() == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    #Set tbl attribute list of columns that must be populated
    checkdf1.tbl.df['Select_blank'] = np.nan
    checkdf1.tbl.nonblank_cols = ['Select_blank', 'Color']

    # Test list with column that is not all populated
    assert checkdf1.LstColsAllNonBlank() == False
    exp = 'ERROR: DataFrame column cannot be blank: Select_blank\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllNonBlank2(checkdf1, capfd):
    """
    .tbl.df list of tbl.nonblank_cols all contain at least one non-blank value (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColNonBlank'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    #Set tbl attribute list of columns that must be populated
    lst = ['id_index', 'Color']

    #Test list with columns that are all populated
    assert checkdf1.LstColsAllNonBlank(df=df_test, lst_cols=lst) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf1.errs.ResetWarning()

    #Set tbl attribute list of columns that must be populated
    checkdf1.tbl.df['Select_blank'] = np.nan
    lst = ['Select_blank', 'Color']

    # Test list with column that is not all populated
    assert checkdf1.LstColsAllNonBlank(df=df_test, lst_cols=lst) == False
    exp = 'custom_ColNonBlank: Select_blank\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColNonBlank1(checkdf1, capfd):
    """
    Specified column contains no non-blank values (True if so)
    JDL 1/11/24; Modified 8/26/24
    """
    # Test a column that contains non-blank values
    assert checkdf1.ColNonBlank('Select') == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test a column that contains only blank values and check error message printout
    checkdf1.tbl.df['Select_blank'] = np.nan
    assert checkdf1.ColNonBlank('Select_blank') == False
    exp = 'ERROR: DataFrame column cannot be blank: Select_blank\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColNonBlank2(checkdf1, capfd):
    """
    Specified column contains no non-blank values (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColNonBlank'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column that contains non-blank values
    assert checkdf1.ColNonBlank('Select', df=df_test) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test a column that contains only blank values and check error message printout
    df_test['Select_blank'] = np.nan
    assert checkdf1.ColNonBlank('Select_blank', df=df_test) == False
    exp = 'custom_ColNonBlank: Select_blank\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllNumeric1(checkdf2, capfd):
    """
    .tbl list of .numeric_cols all numeric values (True if so)
    JDL 8/27/24
    """
    #Set tbl attribute list of columns that must numeric values
    checkdf2.tbl.numeric_cols = [1002, 1003]

    #Test list with columns that are all populated
    assert checkdf2.LstColsAllNumeric() == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf2.errs.ResetWarning()

    #Change a value to a string
    checkdf2.tbl.df.loc[1004, 1002] = 'xyz'

    # Test list with column that is not all populated
    assert checkdf2.LstColsAllNumeric() == False
    exp = 'ERROR: Column must contain only non-null numeric values: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllNumeric2(checkdf2, capfd):
    """
    .tbl list of .numeric_cols all numeric values (True if so)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_ColNumeric'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    #Set tbl attribute list of columns that must be numeric values
    lst = [1002, 1003]

    #Test list with columns that are all populated
    assert checkdf2.LstColsAllNumeric(df=df_test, lst_cols=lst) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf2.errs.ResetWarning()

    #Change a value to a string
    df_test.loc[1004, 1002] = 'xyz'

    # Test list with column that is not all populated
    assert checkdf2.LstColsAllNumeric(df=df_test, lst_cols=lst) == False
    exp = 'custom_ColNumeric: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColNumeric1(checkdf1, capfd):
    """
    Values in a specified column are non-blank and numeric (True if so)
    JDL 1/11/24
    """

    # Test a column that contains only numeric values
    assert checkdf1.ColNumeric('id_index') == True

    # Reset errs to initialized condition and Change a value to a string
    checkdf1.errs.ResetWarning()
    checkdf1.tbl.df.loc['first_row', 'id_index'] = 'xyz'

    # Test the column again
    assert checkdf1.ColNumeric('id_index') == False
    exp = 'ERROR: Column must contain only non-null numeric values: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColNumeric2(checkdf1, capfd):
    """
    Values in a specified column are non-blank and numeric (True if so)
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColNumeric'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column that contains only numeric values
    assert checkdf1.ColNumeric('id_index', df=df_test) == True

    # Reset errs to initialized condition and Change a value to a string
    checkdf1.errs.ResetWarning()
    df_test.loc['first_row', 'id_index'] = 'xyz'

    # Test the column again
    assert checkdf1.ColNumeric('id_index', df=df_test) == False
    exp = 'custom_ColNumeric: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllInNumericRange1(checkdf2, capfd):
    """
    tbls.tbl1.df list of columns' values are within a specified numeric range
    JDL 8/27/24
    """
    #Set tbl attribute list of columns that must numeric values
    lst = [1002, 1003]

    #Test list with columns that whose values are all within the range
    assert checkdf2.LstColsAllInNumericRange(lst, 0., 0.1) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf2.errs.ResetWarning()

    # Test list with column that has value above ulim
    assert checkdf2.LstColsAllInNumericRange(lst, 0., 0.085) == False
    exp = 'ERROR: Column values must be within specified numeric range: 1003\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_LstColsAllInNumericRange2(checkdf2, capfd):
    """
    tbls.tbl1.df list of columns' values are within a specified numeric range
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf2.errs.Locn = 'custom_ColValsInNumericRange'
    checkdf2.IsCustomCodes = True
    df_test = checkdf2.tbl.df

    #Set tbl attribute list of columns that must numeric values
    lst = [1002, 1003]

    #Test list with columns that whose values are all within the range
    assert checkdf2.LstColsAllInNumericRange(lst, 0., 0.1, df=df_test) == True

    # Reset errs to initialized condition and Change a value to NaN
    checkdf2.errs.ResetWarning()

    # Test list with column that has value above ulim
    assert checkdf2.LstColsAllInNumericRange(lst, 0., 0.085, df=df_test) == False
    exp = 'custom_ColValsInNumericRange: 1003\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColValsInNumericRange1(checkdf1, capfd):
    """
    Column values (must be numeric) are within specified range
    JDL 8/26/24
    """
    # Test a column with limits that pass
    assert checkdf1.ColValsInNumericRange('id_index', 1000, 1005) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with limits that fail
    assert checkdf1.ColValsInNumericRange('id_index', 1002, 1004) == False
    exp = 'ERROR: Column values must be within specified numeric range: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColValsInNumericRange2(checkdf1, capfd):
    """
    Column values (must be numeric) are within specified range
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColValsInNumericRange'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column with limits that pass e.g. 1000 to 1005 contains 1002 to 1004
    assert checkdf1.ColValsInNumericRange('id_index', 1000, 1005, df=df_test) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with limits that fail
    assert checkdf1.ColValsInNumericRange('id_index', 1002, 1004, df=df_test) == False
    exp = 'custom_ColValsInNumericRange: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColValsMatchRegex1(checkdf1, capfd):
    """
    Specific table value matches regex pattern
    JDL 8/26/24
    """
    #Example regex pattern for x_y values
    str_regex = '^[a-zA-Z]+_[a-zA-Z]+$'

    #Reset the index to be able to use it for the check
    checkdf1.tbl.df = checkdf1.tbl.df.reset_index(drop=False)

    # Test a column that conforms to the regex pattern
    assert checkdf1.ColValsMatchRegex('Row_Name', str_regex) == True

    # Reset errs to initialized condition and modify to failing value
    checkdf1.errs.ResetWarning()
    checkdf1.tbl.df.loc[0, 'Row_Name'] = 'first.row'

    # Test the column again with values that fail
    assert checkdf1.ColValsMatchRegex('Row_Name', str_regex) == False
    exp = 'ERROR: Column values must match specified pattern: Row_Name\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColValsMatchRegex2(checkdf1, capfd):
    """
    Specific table value matches regex pattern
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColValsMatchRegex'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    #Example regex pattern for x_y values
    str_regex = '^[a-zA-Z]+_[a-zA-Z]+$'

    #Reset the index to be able to use it for the check
    df_test = df_test.reset_index(drop=False)

    # Test a column that conforms to the regex pattern
    assert checkdf1.ColValsMatchRegex('Row_Name', str_regex,  df=df_test) == True

    # Reset errs to initialized condition and modify to failing value
    checkdf1.errs.ResetWarning()
    df_test.loc[0, 'Row_Name'] = 'first.row'

    # Test the column again with values that fail
    assert checkdf1.ColValsMatchRegex('Row_Name', str_regex, df=df_test) == False
    exp = 'custom_ColValsMatchRegex: Row_Name\n'
    check_printout(exp, capfd)


def test_CheckDataFrame_ColContainsListVals1(checkdf1, capfd):
    """
    Individual column contains a specified list of values
    JDL 8/26/24
    """
    # Test a column with list that passes
    assert checkdf1.ColContainsListVals('id_index', [1002, 1003]) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with limits that fail
    assert checkdf1.ColContainsListVals('id_index', [1002, 1005]) == False
    exp = 'ERROR: Column must contain specified list of values: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColContainsListVals2(checkdf1, capfd):
    """
    Individual column contains a specified list of values
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColContainsListVals'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column with list that passes
    assert checkdf1.ColContainsListVals('id_index', [1002, 1003], df=df_test) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with list of values not all in the column
    assert checkdf1.ColContainsListVals('id_index', [1002, 1005], df=df_test) == False
    exp = 'custom_ColContainsListVals: \nMissing: 1005\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColContainsNodupsListVals1(checkdf1, capfd):
    """
    Column does not have duplicates of a list of values
    JDL 8/26/24
    """
    # Test a column with list that passes
    assert checkdf1.ColContainsNodupsListVals('id_index', [1002, 1003]) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with values that fail
    checkdf1.tbl.df.loc['first_row', 'id_index'] = 1002
    assert checkdf1.ColContainsNodupsListVals('id_index', [1002, 1005]) == False
    exp = 'ERROR: Specified list of column values must be unique (no duplicates): \nDuplicate: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_ColContainsNodupsListVals2(checkdf1, capfd):
    """
    Column does not have duplicates of a list of values
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_ColContainsNodupsListVals'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column with list that passes
    assert checkdf1.ColContainsNodupsListVals('id_index', [1002, 1003], df=df_test) == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()

    # Test the column again with values that fail
    checkdf1.tbl.df.loc['first_row', 'id_index'] = 1002
    assert checkdf1.ColContainsNodupsListVals('id_index', [1002, 1005], df=df_test) == False
    exp = 'custom_ColContainsNodupsListVals: \nDuplicate: 1002\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_TableLocMatchesRegex1(checkdf1, capfd):
    """
    Specific table value matches regex pattern
    JDL 8/26/24
    """
    #Example regex pattern for x_y values
    str_regex = '^[a-zA-Z]+_[a-zA-Z]+$'

    #Reset the index to be able to use it for the check
    checkdf1.tbl.df = checkdf1.tbl.df.reset_index(drop=False)
    # Test a column with list that passes
    assert checkdf1.TableLocMatchesRegex('id_index', 1001, 'Row_Name', str_regex) == True

    # Reset errs to initialized condition and modify to failing value
    checkdf1.errs.ResetWarning()
    checkdf1.tbl.df.loc[0, 'Row_Name'] = 'first.row'

    # Test the column again with values that fail
    assert checkdf1.TableLocMatchesRegex('id_index', 1001, 'Row_Name', str_regex) == False
    exp = 'ERROR: Specified table cell must match pattern: \nNon-match: first.row\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_TableLocMatchesRegex2(checkdf1, capfd):
    """
    Specific table value matches regex pattern
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_TableLocMatchesRegex'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    #Example regex pattern for x_y values
    str_regex = '^[a-zA-Z]+_[a-zA-Z]+$'

    #Reset the index to be able to use it for the check
    df_test = df_test.reset_index(drop=False)
    # Test a column with list that passes
    assert checkdf1.TableLocMatchesRegex('id_index', 1001, 'Row_Name', \
                                             str_regex, df=df_test) == True

    # Reset errs to initialized condition and modify to failing value
    checkdf1.errs.ResetWarning()
    df_test.loc[0, 'Row_Name'] = 'first.row'

    # Test the column again with values that fail
    assert checkdf1.TableLocMatchesRegex('id_index', 1001, 'Row_Name', \
                                             str_regex, df=df_test) == False
    exp = 'custom_TableLocMatchesRegex: \nNon-match: first.row\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateColVals1(checkdf1, capfd):
    """
    Check if values in a specified column are within a specified numeric range
    JDL 8/26/24
    """
    # Test a column with list that passes
    assert checkdf1.NoDuplicateColVals('id_index') == True

    # Reset errs to initialized condition
    checkdf1.errs.ResetWarning()
    checkdf1.tbl.df.loc[0, 'id_index'] = 1002

    # Test the column again with limits that fail
    assert checkdf1.NoDuplicateColVals('id_index') == False
    exp = 'ERROR: DataFrame Column values must be unique: id_index\n'
    check_printout(exp, capfd)

def test_CheckDataFrame_NoDuplicateColVals2(checkdf1, capfd):
    """
    Check if values in a specified column are within a specified numeric range
    (Custom error codes; check df instead of tbl.df)
    JDL 8/27/24
    """
    #Set custom error codes flag, lookup Locn, and df
    checkdf1.errs.Locn = 'custom_NoDuplicateColVals'
    checkdf1.IsCustomCodes = True
    df_test = checkdf1.tbl.df

    # Test a column that does not have duplicate values
    assert checkdf1.NoDuplicateColVals('id_index', df=df_test) == True

    # Reset errs to initialized condition and modify to create duplicate val
    checkdf1.errs.ResetWarning()
    df_test.loc[0, 'id_index'] = 1002

    # Test the column again with limits that fail
    assert checkdf1.NoDuplicateColVals('id_index', df=df_test) == False
    exp = 'custom_NoDuplicateColVals: id_index\n'
    check_printout(exp, capfd)

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

def test_CheckExcelFiles_CheckFilesProcedure1(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (1) Check of case where there are no errors
    """
    check_files.lst_shts = [['first_sheet', 'second_sheet']]
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

    if IsPrint & (not check_files.IsWbErr): print('\n\nNo errors\n')

def test_CheckExcelFiles_CheckFilesProcedure2(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class 
    (2) non-existent file
    """
    check_files.lst_files = ['xxxx.xlsx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not found'

    if IsPrint: print_msgs_accum(check_files)

def test_CheckExcelFiles_CheckFilesProcedure3(check_files):
    """
    Test the CheckFilesProcedure method of the CheckExcelFiles class
    (3) non-Excel file
    """
    check_files.lst_files = ['../tests/dummy_file.docx']
    check_files.CheckFilesProcedure()
    assert check_files.IsWbErr == True
    assert check_files.errs.Msgs_Accum[0:27] == 'ERROR: Input file not a val'

    if IsPrint: print_msgs_accum(check_files)

def test_CheckExcelFiles_CheckFilesProcedure4(check_files):
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

def test_CheckExcelFiles_ExcelFileExists1(check_files):
    """
    Check if each Excel file exists and can be opened
    JDL 1/3/24
    """
    # instance CheckExcelFiles and check for file presence
    check_files.ExcelFileExists(idx=0)

    # Check that no error was recorded
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

def test_CheckExcelFiles_ExcelFileExists2(check_files):
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

def test_CheckExcelFiles_ExcelFileOpens1(check_files):
    """
    Check if Excel file opens successfully
    JDL 1/4/24
    """
    # Check file opens for valid Excel file
    check_files.ExcelFileOpens(idx=0)
    assert check_files.IsWbErr == False
    assert len(check_files.errs.Msgs_Accum) == 0

def test_CheckExcelFiles_ExcelFileOpens2(check_files):
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

def test_CheckExcelFiles_AllSheetsExist1(check_files):
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

def test_CheckExcelFiles_AllSheetsExist2(check_files):
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

def test_CheckExcelFiles_SheetExists(check_files):
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