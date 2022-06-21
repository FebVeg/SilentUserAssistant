
############################################################################################
# Use C# [System.Security.Cryptography.RNGCryptoServiceProvider] from Powershell on Python #
############################################################################################


import subprocess


def generate_key():
    
    ''' Generate a 32 Bytes AES Key and a 16 Bytes InitializationVector '''

    pscode = \
        """
        $RNG = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
        $AESEncryptionKey     = [System.Byte[]]::new(32)
        $InitializationVector = [System.Byte[]]::new(16)
        $RNG.GetBytes($AESEncryptionKey)
        $RNG.GetBytes($InitializationVector)
        $AESEncryptionKey
        $InitializationVector
        $RNG.Dispose()
        """

    powershell_output = subprocess.run(["powershell", "-Command", pscode], capture_output=True)  
    output  = powershell_output.stdout.decode().strip().splitlines()
    key     = output[0:32]
    iv      = output[-16:]

    return str(key).replace('[', '').replace(']', ''), str(iv).replace('[', '').replace(']', '')


def encrypt(string, key = None, iv = None):

    ''' Enrypt a string using Powershell [System.Security.Cryptography.AesCryptoServiceProvider] '''

    if key:
        _key = key
    else:
        _key = "'141', '39', '117', '153', '219', '221', '208', '174', '11', '169', '15', '20', '173', '150', '240', '236', '33', '103', '209', '201', '2', '31', '49', '221', '123', '171', '62', '81', '120', '157', '232', '17'"

    if iv:
        _iv = iv
    else:
        _iv = "'237', '68', '14', '38', '86', '129', '185', '146', '63', '21', '193', '64', '21', '191', '120', '207'"

    pscode = \
        """
        $AESCipher            = New-Object System.Security.Cryptography.AesCryptoServiceProvider
        $AESCipher.Key        = @({0})
        $AESCipher.IV         = @({1})
        $UnencryptedBytes     = [System.Text.Encoding]::UTF8.GetBytes('{2}')
        $Encryptor            = $AESCipher.CreateEncryptor()
        $EncryptedBytes       = $Encryptor.TransformFinalBlock($UnencryptedBytes, 0, $UnencryptedBytes.Length)
        [byte[]] $FullData    = $AESCipher.IV + $EncryptedBytes
        $CipherText           = [System.Convert]::ToBase64String($FullData)
        $AESCipher.Dispose()
        $CipherText
        """.format(_key, _iv, string)

    powershell_output = subprocess.run(["powershell", "-Command", pscode], capture_output=True)  
    output = powershell_output.stdout.decode().strip()
    return output


def decrypt(string, key = None):

    ''' Decrypt a string using Powershell [System.Security.Cryptography.AesCryptoServiceProvider] '''

    if key:
        _key = key
    else:
        _key = "'141', '39', '117', '153', '219', '221', '208', '174', '11', '169', '15', '20', '173', '150', '240', '236', '33', '103', '209', '201', '2', '31', '49', '221', '123', '171', '62', '81', '120', '157', '232', '17'"

    pscode = \
        """
        $AESCipher            = New-Object System.Security.Cryptography.AesCryptoServiceProvider
        $AESCipher.Key        = @({0})
        $EncryptedBytes       = [System.Convert]::FromBase64String('{1}')
        $AESCipher.IV         = $EncryptedBytes[0..15]
        $Decryptor            = $AESCipher.CreateDecryptor();
        $UnencryptedBytes     = $Decryptor.TransformFinalBlock($EncryptedBytes, 16, $EncryptedBytes.Length - 16)
        $MySecretText         = [System.Text.Encoding]::UTF8.GetString($UnencryptedBytes)
        $AESCipher.Dispose()
        $MySecretText

        """.format(_key, string)

    powershell_output = subprocess.run(["powershell", "-Command", pscode], capture_output=True)  
    output = powershell_output.stdout.decode().strip()
    return output


def encrypt_content_of_file(input_file):
    pscode = \
        f"""
        $aesKey     = (2,3,1,4,54,32,144,23,5,3,1,41,36,31,18,175,6,17,1,9,5,1,76,23)
        $plaintext  = Get-Content -Path "{input_file}" -Raw
        $Secure     = ConvertTo-SecureString -String $plaintext -AsPlainText -Force
        $encrypted  = ConvertFrom-SecureString -SecureString $Secure -Key $aesKey

        $encrypted
        """.replace('        ', '')

    powershell_output = subprocess.run(["powershell", "-Command", pscode], capture_output=True)  
    output = powershell_output.stdout.decode().strip()
    return output


def decrypt_content_of_file(input_file):
    pscode = \
        f"""
        $encrypted      = Get-Content -Path "{input_file}" -Raw
        $aesKey         = (2,3,1,4,54,32,144,23,5,3,1,41,36,31,18,175,6,17,1,9,5,1,76,23)
        $secureObject   = ConvertTo-SecureString -String $encrypted -Key $aesKey
        $decrypted      = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureObject)
        $decrypted      = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($decrypted)
        $decrypted
        """.replace('        ', '')

    powershell_output = subprocess.run(["powershell", "-Command", pscode], capture_output=True)  
    output = powershell_output.stdout.decode().strip()
    return output
