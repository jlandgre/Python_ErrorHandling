'Class for error handling in cascaded function architecture
'Version 6/7/23 - Add ShowMessage and FlagError
'Version 7/10/23 - Fix bug with ShowMessage args
'Version 8/29/23 - Refactor to eliminate errs as argument; Modify LookupCommentMsg args
'Version 11/21/23 - Mods to .RecordErr(), .AppendErrMsg() to clean up user-facing msgs

Option Explicit

Public IsHandle As Boolean 'Toggle error handling on/off
Public IsDriver As Boolean 'Trigger stack tracing messaging for nested functions
Public IsNewErr As Boolean 'Trigger handling of new error versus stack tracing
Public IsUserFacing As Boolean 'True for user-facing error messaging (versus VBA stack
                               'tracing reporting)
Public Locn As String 'Current sub or function Error locn
Public iCodeLocal As Integer 'Raw error code - integer set in routine where error occurs
Public iCodeBase As Integer
Public iCodeReport As Integer 'Lookup table error code (composite sub/function base code + iCode)
Public ErrParam As String 'Optional param value to report in messaging; typically assign in code
                          'where error occurs
Public ErrMsg As String 'Error message string --constructed by AppendErrMsg() class method
Public wkbk As Workbook 'Application workbook; same as wkbkE if contains shtErrors lookup table
Public wkbkE As Workbook 'Workbook containing shtErrors lookup table (optionally can be add-in)
Public wkshtActive As Worksheet 'Initial active sheet - to reset at end of execution
'------------------------------------------------------------------------------------------------
'Initialize errs Class
' Declare errs as global prior to first, user-initiated procedure sub (Public errs as Object)
' Call errs.Init from user-initiated sub after instancing errs (dim errs as New ErrorHandling)
'
'JDL 12/20/22
'
Public Sub Init(Optional IsHandle)
    With errs
        If IsMissing(IsHandle) Then
            .IsHandle = True
        Else
            .IsHandle = IsHandle
        End If
        Set .wkbk = ThisWorkbook
        Set .wkbkE = ThisWorkbook
        
        .Locn = ""
        .iCodeLocal = 0
        .iCodeBase = 0
        .iCodeReport = 0
        .ErrParam = ""
        .ErrMsg = ""
        .IsUserFacing = False
        .IsNewErr = True
        .IsDriver = False
    End With
End Sub
'-----------------------------------------------------------------------------------------------
' Record new error or append stack track message
'
' Inputs:   Locn [String] sub or function where error occurred
'         IsDriver [Boolean] True if Locn is a driver sub
'
' Created:  2/17/21 JDL      Modified: 11/21/23 modify If .IsNewErr Else logic
'
Sub RecordErr(Locn, Optional ByRef CallingFunction)
    Dim sMsgSuffix As String, IsDriver As Boolean
    With errs
    
        If IsMissing(CallingFunction) Then
            errs.IsDriver = True
        
        'Return False for Boolean calling function (to signify error)
        Else
            CallingFunction = False
        End If
    
        'Log error location; lookup base code and get iCodeReport for message lookup
        If .IsNewErr Then
            .Locn = Locn
            If GetBaseErrCode() Then .iCodeReport = .iCodeBase + .iCodeLocal
            
        'Record tracing for possible non user-facing message
        ElseIf Not .IsUserFacing Then
            sMsgSuffix = "Called by " & Locn
        End If
    
        'Append to the error message
        AppendErrMsg sMsgSuffix
        
        'report error if called by a driver sub
        If .IsDriver Then .ReportMsg
    End With
End Sub
'-----------------------------------------------------------------------------------------------
' Append error message updates onto ErrMsg
'
'Inputs:    sMsgSuffix [String] Name of calling routine - to trace stack if non user-facing
'
' Created:   2/17/21 JDL      Modified: 11/21/23 Modify logic for IsUserFacing elim vbCrLf
'
Function AppendErrMsg(sMsgSuffix) As Boolean
    Dim aryMetaData As Variant, sMsgNew As String

    With errs
    
        'If new (root) error, look it up and populate its message
        If .IsNewErr Then
    
            'Look up Error table metadata by iCodeReport
            aryMetaData = .aryErrLookup()
            If Len(aryMetaData(3)) > 0 Then .IsUserFacing = aryMetaData(3)
            
            'If Base error code, set string denoting VBA Error
            If aryMetaData(2) = sErrBase Then aryMetaData(2) = sVBAErr
            
            'Add additional line feed to message if there are already accumulated warning(s)
            If Len(.ErrMsg) > 0 Then .ErrMsg = .ErrMsg & vbCrLf
    
            'If code is found, message string is iCode + Routine + sMsg + sVal
            If aryMetaData(0) = iErrNotFound Then
                If .iCodeBase <> iErrNotFound Then
                    sMsgNew = .Locn & " Error code not found: " & .iCodeBase
                Else
                    sMsgNew = "Base error code not found for routine: " & .Locn
                End If
            
            'Assign custom message based on either developer or user-facing
            Else
                If Not .IsUserFacing Then
                    sMsgNew = "Error " & .iCodeReport & "; in sub or function, "
                    If Len(aryMetaData(1)) > 0 Then sMsgNew = sMsgNew & aryMetaData(1) & vbCrLf
                    If Len(aryMetaData(2)) > 0 Then sMsgNew = sMsgNew & aryMetaData(2) & .ErrParam & vbCrLf
                ElseIf Len(aryMetaData(2)) > 0 Then
                    sMsgNew = aryMetaData(2)
                    If Len(.ErrParam) > 0 Then sMsgNew = sMsgNew & .ErrParam
                End If
            End If
            .ErrMsg = .ErrMsg & sMsgNew
            .IsNewErr = False
    
        'If Not a new error and not a driver error, append calling routine name
        ElseIf Not .IsUserFacing Then
            .ErrMsg = .ErrMsg & sMsgSuffix & vbCrLf
        End If
    End With
End Function
'-----------------------------------------------------------------------------------------------
' Lookup metadata from Errors table
'
' Created:  2/17/21 JDL      Modified: 12/20/22 for ErrorHandling Class
'
Function aryErrLookup() As Variant
    Dim ary As Variant, rng As Range, rngRows As Range
    Dim colrngCode As Range, colrngFunc As Range, colrngMsg As Range, colrngIMsg As Range

    SetTblELocations colrngFunc, colrngMsg, colrngCode, colrngIMsg, rngRows

    'Look up the Error code
    With errs
        .iCodeReport = .iCodeBase + errs.iCodeLocal
        Set rng = rngMultiKeyBasic(rngRows, Array(colrngCode), Array(.iCodeReport))

        'Default - Code not found
        ary = Array(iErrNotFound, "", "Msg Not Found", "", "", False)

        'Populate the Code's metadata into returned array
        If Not rng Is Nothing Then
            ary = Array(Intersect(rng, colrngCode).Value, Intersect(rng, colrngFunc).Value, _
                Intersect(rng, colrngMsg).Value, Intersect(rng, colrngIMsg).Value)
        End If
    End With
    aryErrLookup = ary
End Function
'------------------------------------------------------------------------------------------------
' Report Errors to user (Call from ErrorExit at end of first, user-initiated procedural routine)
'
' Modified JDL 12/13/22
'
Public Sub ReportMsg()
    Dim sMsg As String, sTitle As String, i As Integer
    With errs
        If Not errs.IsHandle Then Exit Sub
        
        'Show either default or error-specific message
        sTitle = "Execution Error"
        i = MsgBox(errs.ErrMsg, vbOKOnly + vbCritical, sTitle)
        
        'Reset (global) IsDriver for next usage
        Set errs = Nothing
    End With
End Sub
'-----------------------------------------------------------------------------------------------
' Configure and report warnings
'
' Created:  6/8/21 JDL      Modified: 6/8/23 Add & errs.ErrParam to sMsg
'                                     7/10/23 remove errs argument and ary variable
'
Sub ReportWarningMsg(iCode, Locn)
    Dim sMsg As String, sTitle As String, i As Integer
    With errs
    
        'Set errs params to enable looking up message to display
        .Locn = Locn
        .iCodeLocal = iCode
        
        'Look up and display the message
        .GetBaseErrCode errs
        If .iCodeBase = iErrNotFound Then Exit Sub
        'ary = .aryErrLookup()
        sMsg = .aryErrLookup()(2) & errs.ErrParam
        sTitle = "Warning/Information"
        i = MsgBox(sMsg, vbOKOnly + vbInformation, sTitle)
        
        'Re-initialize to be ready for a new error
        .Init IsHandle:=.IsHandle
    End With
End Sub
'-----------------------------------------------------------------------------------------------
' Create and return a comment message for specified cell range
' IsReinitialize=False retains .iCodeLocal to comment multiple cells
'
' Created:   7/30/21 JDL     Modified: 12/20/22 for ErrorHandling Class; 8/29/23 elim errs arg
'                                       and add IsReinitialize arg
'
Sub LookupCommentMsg(rng, Locn, Optional IsReinitialize = True)
    Dim sMsg As String
    With errs
        .Locn = Locn
        
        'Get the Base Error code for .LocnReport; use for Msg lookup
        .GetBaseErrCode
        If .iCodeBase <> iErrNotFound Then
            AddComment rng, .aryErrLookup()(2)
        End If
        
        'Re-initialize to be ready for a new error
        If IsReinitialize Then .Init IsHandle:=.IsHandle
    End With
End Sub
'-----------------------------------------------------------------------------------------------
' Get the base error code for a specified routine
'
' Created:  2/17/21 JDL      Modified: 12/21/22 for ErrorHandling Class and non tblRowsCols
'                                       8/29/23 eliminate errs argument
'
Function GetBaseErrCode() As Boolean
    Dim R As Range, rngRows As Range
    Dim colrngCode As Range, colrngFunc As Range, colrngMsg As Range, colrngIMsg As Range

    With errs
        SetTblELocations colrngFunc, colrngMsg, colrngCode, colrngIMsg, rngRows
        Set R = rngMultiKeyBasic(rngRows, Array(colrngFunc, colrngMsg), Array(.Locn, sErrBase))
            .iCodeBase = iErrNotFound
            If Not R Is Nothing Then .iCodeBase = Intersect(R, colrngCode)
            If .iCodeBase <> iErrNotFound Then GetBaseErrCode = True
    End With
End Function
'-----------------------------------------------------------------------------------------------
Sub SetTblELocations(colrngFunc, colrngMsg, colrngCode, colrngIMsg, rngRows)
    Dim c As Range
    With errs.wkbkE.Sheets(shtErrors)
        Set colrngCode = .Columns(1)
        Set colrngFunc = .Columns(3)
        Set colrngMsg = .Columns(4)
        Set colrngIMsg = .Columns(6)
    End With
    With errs.wkbkE.Sheets(shtErrors).Columns(1)
        Set c = .Cells(.Cells.Count).End(xlUp)
    End With
    Set rngRows = Range(errs.wkbkE.Sheets(shtErrors).Rows(2), c.EntireRow)
End Sub
'-----------------------------------------------------------------------------------------------
'Assign error code based on Boolean argument and set ErrorHandling attributes
'
' Inputs: IsError [Boolean] Boolean expression; evaluates to True if error
'         iCode [Integer] local error code in case IsError = True
'                         "Local" refers to local to calling function or sub
'         ErrParam [Variant] optional parameter to report with message
'
' Created:  6/8/21 JDL   Modified 11/21/23 Clean up logic and Add Optional ErrParam argument
'
Function IsFail(IsError, iCode, Optional ErrParam) As Boolean
    IsFail = False
    If Not IsError Then Exit Function
    
    IsFail = True
    errs.iCodeLocal = iCode
    If Not IsMissing(ErrParam) Then errs.ErrParam = ErrParam
End Function
'-----------------------------------------------------------------------------------------------
' Create and return user response from msgbox prompt
'
' Created:   7/20/21 JDL; 6/7/23 adapt to ErrorHandling Class
'                         7/10/23 fix bug by eliminate errs as argument
'
' Inputs:   Locn [String] name of calling routine (for Errors_ lookup)
'         iCode [Integer] local error code ( iCode + errs.iCodeBase = errs.iCodeReport)
'         vbType [Integer] VBA MsgBox function buttons argument (e.g. vbCritical + vbOK = 17)
'
Function ShowMessage(Locn As String, iCode As Integer, vbType As Integer)
    Dim iMsg As Integer, sMsg As String, sTitle As String, aryMsg As Variant, ary As Variant
    
    'Default message and title
    sMsg = "Base Error Code Not Found: " & Locn
    sTitle = "Missing Base Code"
    
    'Look up message based on Locn and iCode
    With errs
        .Locn = Locn
        If .GetBaseErrCode() <> iErrNotFound Then
            .iCodeLocal = iCode
            sMsg = .aryErrLookup()(2)
            
            'Set Title and Msg based by splitting
            .setMsgTitleAndText sMsg, sTitle
        End If
    End With
    ShowMessage = MsgBox(sMsg, vbType, sTitle)
End Function
'-----------------------------------------------------------------------------------------------
' Split a Setting or Error message into Title and Text parts
'
'
Sub setMsgTitleAndText(ByRef sMsg As String, ByRef sTitle As String)
    Dim aryMsg As Variant
    
    aryMsg = Split(sMsg, "|")
    If UBound(aryMsg) = 0 Then Exit Sub
    
    'Set parts if array has two parts
    sTitle = aryMsg(0)
    sMsg = aryMsg(1)
End Sub
'-----------------------------------------------------------------------------------------------
' Delete previous warnings/errors file and Reset errors/warnings setting
'
' Created:   7/7/21 JDL      Modified: 6/12/23 migrate to ErrorHandling class
'
Sub ResetWarningsAndErrors(wkbk, sSelf, Optional ByVal IsVal)
    Dim sPath As String, sString
    If IsMissing(IsVal) Then IsVal = False
    
    'Delete previous IsAuto WarningsAndErrors.txt file if any
    'sPath = wkbk.Path & "\" & sFileErrs        ' onedrive path mitigation
    sPath = ReadSetting(wkbk, "LocalPath")
    sPath = BuildPath(sPath, sFileErrs)
    If Len(Dir(sPath)) > 0 Then Kill sPath
    
    'Initialize a Setting for new warnings and errors
    sString = ParseNow & " " & sSelf
    If IsVal Then sString = sSelf & " Validation"
    UpdateSetting wkbk, sSettingErrs, sString & vbCrLf
End Sub
'-----------------------------------------------------------------------------------------------
'Purpose:   Parse current timestamp into a fixed-length string
'
'Created:   2/15/22 JDL
'
'Output format: YYYYMMDD_HHMM_SS (length = 16 characters)
'
Function ParseNow() As String
    Dim dNow As Date, ary As Variant, s As Variant
    dNow = Now
    ary = Array(Year(dNow), Month(dNow), Day(dNow))
    For Each s In ary
        If Len(s) = 1 Then s = "0" & s
        ParseNow = ParseNow & s
    Next s
    ParseNow = ParseNow & "_"
    ary = Array(Hour(dNow), Minute(dNow))
    For Each s In ary
        If Len(s) = 1 Then s = "0" & s
        ParseNow = ParseNow & s
    Next s
    
    'Add Seconds
    s = Second(dNow)
    If Len(s) = 1 Then s = "0" & s
    ParseNow = ParseNow & "_" & s
End Function
'-----------------------------------------------------------------------------------------------
' Write accumulated warnings and errors to file
'
'Inputs: wkbk [Workbook object]
'        IsVal [Boolean] True if validation run (used to create stable/repeatable output)
'
'Created:   7/7/21 JDL  Modified: 2/24/22 JDL IsVal = False by default if missing
'                                 4/5/22 ThiswWorkbook.Path as default; clarify sNow formula
'                                 6/12/23 move to ErrorHandling class
'
Sub WriteErrorsToFile(wkbk, IsVal)
    Dim sPathFile As String, sErrs As String, sNow As String
    
    If IsMissing(IsVal) Then IsVal = False
    sErrs = ReadSetting(wkbk, sSettingErrs)
    sPathFile = ReadSetting(wkbk, "LocalPath")
    If Len(sPathFile) < 1 Then sPathFile = ThisWorkbook.Path
        
    'Set suffix for filename: either datetime or "Val"
    If IsVal Then
        sNow = "_Val"
    ElseIf Len(sErrs) > 0 Then
        sNow = "_" & Left(sErrs, 16)
    End If
    sPathFile = sPathFile & "\" & sFileErrs & sNow & ".txt"
            
    Call WriteFile(sPathFile, sErrs)
    DeleteSetting wkbk, sSettingErrs
End Sub


