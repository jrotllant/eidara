' DARA Watcher — Silent Launcher
' Runs watcher.py in the background without a console window.
' Used by Task Scheduler for automatic startup.
Set WshShell = CreateObject("WScript.Shell")
strPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "")
WshShell.Run "python """ & strPath & "watcher.py""", 0, False
