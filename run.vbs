Option Explicit

Dim objShell, objFSO, strScriptPath, strParentFolder, strCommand
Dim strPythonExe, strPort, strBrowserUrl, objHTTP
Dim intRetryCount, intMaxRetries, isServerRunning

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
Set objHTTP = CreateObject("MSXML2.XMLHTTP")

' 1. VBS自身が存在するディレクトリを基準にする
strScriptPath = WScript.ScriptFullName
strParentFolder = objFSO.GetParentFolderName(strScriptPath)
objShell.CurrentDirectory = strParentFolder

strPythonExe = "bin\pythonw.exe"
If Not objFSO.FileExists(strPythonExe) Then
    MsgBox "Python環境が見つかりません。" & vbCrLf & "最初に setup.bat を実行して環境を構築してください。", 48, "セットアップ未完了"
    WScript.Quit
End If

strPort = "5000"
strBrowserUrl = "http://127.0.0.1:" & strPort

' 5. 二重起動を検出し、すでにサーバーが起動していればブラウザだけを開く
isServerRunning = False
On Error Resume Next
objHTTP.Open "GET", strBrowserUrl, False
objHTTP.Send
If Err.Number = 0 Then
    If objHTTP.Status = 200 Then
        isServerRunning = True
    End If
End If
Err.Clear
On Error GoTo 0

If isServerRunning Then
    objShell.Run strBrowserUrl
    WScript.Quit
End If

' 2. Pythonバックエンドを非表示で起動する
If Not objFSO.FolderExists("data") Then
    objFSO.CreateFolder("data")
End If
strCommand = "cmd /c """ & strPythonExe & " core\app.py > data\app.log 2>&1"""
objShell.Run strCommand, 0, False

' 3. サーバーの起動完了を待つ (最大10秒)
intMaxRetries = 20
intRetryCount = 0
isServerRunning = False

Do While intRetryCount < intMaxRetries
    WScript.Sleep 500
    
    On Error Resume Next
    objHTTP.Open "GET", strBrowserUrl, False
    objHTTP.Send
    If Err.Number = 0 Then
        If objHTTP.Status = 200 Then
            isServerRunning = True
            Exit Do
        End If
    End If
    Err.Clear
    On Error GoTo 0
    
    intRetryCount = intRetryCount + 1
Loop

' 4. 既定ブラウザでアプリを開く
If isServerRunning Then
    objShell.Run strBrowserUrl
Else
    MsgBox "サーバーの起動に失敗しました。" & vbCrLf & "data\app.log を確認してください。", 16, "起動エラー"
End If
