Option Explicit
'This module contains user-initiated driver subroutines - Modified 11/21/23
'-----------------------------------------------------------------------------------------------
'-----------------------------------------------------------------------------------------------
'   Demo of error handling for a top-level driver subroutine error (user-facing message)
'
Public Sub DriverExample()
    
    'Initialize Global Error handling (if not already instanced)
    SetErrorHandle "driver": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer
    
    'Set Application and Workbook status to optimize performance
    wkbkResetStatus True, ThisWorkbook, xCalculation

    '<<< Code to do application use case >>>
    
    'A known error condition occurs
    '(IsFail True aka Boolean expression that evaluates to True signifies error)
    If errs.IsFail(True, 1) Then GoTo ErrorExit

    'Reset Application status following successful execution
    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    errs.RecordErr "DriverExample"
End Sub
'-----------------------------------------------------------------------------------------------
'-----------------------------------------------------------------------------------------------
'   Demo of error in nested function (user-facing message)
'
Public Sub DriverNestedExample()
    SetErrorHandle "driver": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer
    wkbkResetStatus True, ThisWorkbook, xCalculation

    'Call a nested function to do something
    If Not FirstNested() Then GoTo ErrorExit

    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    errs.RecordErr "DriverNestedExample"
End Sub
'-----------------------------------------------------------------------------------------------
'   First level nested function
'   Use Boolean functions to report success/failure back to calling routine
'
Public Function FirstNested() As Boolean
    SetErrorHandle FirstNested: If errs.IsHandle Then On Error GoTo ErrorExit
    Dim IsOk As Boolean
    
    '<<code to do application use case; test for error that doesn't occur>>
    IsOk = True
    If errs.IsFail(Not IsOk, 1) Then GoTo ErrorExit
    
    'Call second level function to do additional tasks
    If Not SecondNested() Then GoTo ErrorExit
    Exit Function
    
ErrorExit:
    errs.RecordErr "FirstNested", FirstNested
End Function
'-----------------------------------------------------------------------------------------------
'   Second level nested function (fatal error occurs here)
'
Public Function SecondNested() As Boolean
    SetErrorHandle SecondNested: If errs.IsHandle Then On Error GoTo ErrorExit
    Dim IsOk As Boolean

    '<<code to do application task>>
    
    'test for error that does occur
    IsOk = False
    If errs.IsFail(Not IsOk, 1) Then GoTo ErrorExit
    Exit Function
    
ErrorExit:
    errs.RecordErr "SecondNested", SecondNested
End Function
'-----------------------------------------------------------------------------------------------
'-----------------------------------------------------------------------------------------------
'   Demo of VBA error in nested function (developer-facing stack trace messaging)
'
Public Sub DriverVBAErrExample()
    SetErrorHandle "driver": If errs.IsHandle Then On Error GoTo ErrorExit
    Dim xCalculation As Integer
    wkbkResetStatus True, ThisWorkbook, xCalculation

    'Call a nested function to do something
    If Not FirstNested2() Then GoTo ErrorExit

    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    wkbkResetStatus True, ThisWorkbook, xCalculation
    errs.RecordErr "DriverVBAErrExample"
End Sub
'-----------------------------------------------------------------------------------------------
'   First level nested function
'   Use Boolean functions to report success/failure back to calling routine
'
Public Function FirstNested2() As Boolean
    SetErrorHandle FirstNested2: If errs.IsHandle Then On Error GoTo ErrorExit
    Dim IsOk As Boolean
    
    '<<code to do application use case; test for error that doesn't occur>>
    
    'Call second level function to do additional tasks
    If Not SecondNestedVBAErr() Then GoTo ErrorExit
    Exit Function
    
ErrorExit:
    errs.RecordErr "FirstNested2", FirstNested2
End Function
'-----------------------------------------------------------------------------------------------
'   Second level nested function (fatal error occurs here)
'
Public Function SecondNestedVBAErr() As Boolean
    SetErrorHandle SecondNestedVBAErr: If errs.IsHandle Then On Error GoTo ErrorExit
    Dim IsOk As Boolean, i As Integer

    '<<code to do application task>>
    
    'test for error that does not occur
    IsOk = False
    If errs.IsFail(IsOk, 1) Then GoTo ErrorExit
    
    'Induce an "unexpected" VBA error
    i = 1 / 0
    Exit Function
    
ErrorExit:
    errs.RecordErr "SecondNestedVBAErr", SecondNestedVBAErr
End Function
'-----------------------------------------------------------------------------------------------
'-----------------------------------------------------------------------------------------------
'   Demo of displaying an informational message/non-fatal warning
'
Public Sub DriverJustAWarning()
    SetErrorHandle "non-bool": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer
    wkbkResetStatus True, ThisWorkbook, xCalculation
    
    '<<< Code to do application use case >>>
    
    'Display a non-fatal warning/informational advice
    errs.ReportWarningMsg 2, "DriverJustAWarning"

    'Reset Application status following successful execution
    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    wkbkResetStatus True, ThisWorkbook, xCalculation
    errs.RecordErr "DriverJustAWarning"
End Sub
'-----------------------------------------------------------------------------------------------
'-----------------------------------------------------------------------------------------------
'   Demo of showing a cell comment and an error message to direct user to look at comment
'
Public Sub CellCommentMessage()
    SetErrorHandle "non-bool": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer, c As Range, IsInputOK As Boolean
    wkbkResetStatus True, ThisWorkbook, xCalculation

    '<<< Code to do application use case >>>
    
    'Some problem occurred that should be flagged in input cell
    IsInputOK = False
    Set c = ThisWorkbook.Sheets("Demo").Cells(19, 5)
    If errs.IsFail(Not IsInputOK, 2) Then GoTo FlagWithComment
    
    'Reset Application status following successful execution
    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
FlagWithComment:

    'Add a cell comment to the Example Input cell
    errs.LookupCommentMsg c, "CellCommentMessage"
    
    'Also display an error dialog to alert user
    errs.iCodeLocal = 3
    '(control passes to ErrorExit unless redirected otherwise with Exit Function etc.)
    
ErrorExit:
    wkbkResetStatus True, ThisWorkbook, xCalculation
    errs.RecordErr "CellCommentMessage"
End Sub
'-----------------------------------------------------------------------------------------------
'   Report optional parameter - 11/21/23
'   User-facing error reported with additional info such as error location etc.
'
Public Sub OptionalParamExample()
    
    'Initialize Global Error handling (if not already instanced)
    SetErrorHandle "driver": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer
    
    'Set Application and Workbook status to optimize performance
    wkbkResetStatus True, ThisWorkbook, xCalculation

    '<<< Code to do application use case >>>
    
    'A known error condition occurs
    If errs.IsFail(True, 1, ErrParam:="Additional info") Then GoTo ErrorExit

    'Reset Application status following successful execution
    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    errs.RecordErr "OptionalParamExample"
End Sub
'-----------------------------------------------------------------------------------------------
'   Report optional parameter with non-user-facing error - 11/21/23
'
Public Sub OptionalParamExample2()
    
    'Initialize Global Error handling (if not already instanced)
    SetErrorHandle "driver": If errs.IsHandle Then On Error GoTo ErrorExit
    
    Dim xCalculation As Integer
    
    'Set Application and Workbook status to optimize performance
    wkbkResetStatus True, ThisWorkbook, xCalculation

    '<<< Code to do application use case >>>
    
    'A known error condition occurs
    If errs.IsFail(True, 1, ErrParam:="Additional info") Then GoTo ErrorExit

    'Reset Application status following successful execution
    wkbkResetStatus True, ThisWorkbook, xCalculation
    Exit Sub
    
ErrorExit:
    errs.RecordErr "OptionalParamExample2"
End Sub

Public Sub DeleteComment()
    ThisWorkbook.Sheets("Demo").Cells(19, 5).ClearComments
End Sub
