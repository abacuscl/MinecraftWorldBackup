#Imports
import os
import sys
import datetime
import time
import shutil
from pathlib import Path
from threading import Thread, Event

#Variables
DEFAULT_SAVEDIR = f"{Path.home()}\\Appdata\\Roaming\\.minecraft\\saves"
DEFAULT_BACKUPDIR = f"{Path.home()}\\Appdata\\Roaming\\.minecraft\\saves\\backups"
DEFAULT_FREQ = 5
DEFAULT_KEPT = 5
VERSION = "v1.1.0"

app_dir = ""
save_dir = ""
backup_dir = ""
backup_freq = -1
ver_kept = -1
selected_world = ""
current_mode = 0
runnable = True
quit_autosave = ""

'''
Startup Methods
'''
#The main method that runs the application
def run():
    global current_mode
    global runnable

    #Initialize the application
    init()

    #Run the app
    while True:

        #If the app can run without errors then run the program
        printHello()
        while runnable:
            if current_mode == 0:
                current_mode = getMode()
            elif current_mode == 1:
                copySave()
            elif current_mode == 2:
                backupSave()
            elif current_mode == 3:
                autoBackupSave()

        #Otherwise, there may be an error and prompt the user to correct it
        print("The config file or backups folder was unable to be verified\n")
        print("Type config to open the config file and make changes")
        print("Type regenerate to regenerate the config file")
        print("Type recreate to attempt to recreate the backups folder\n")
        print("When changes are made, type reload to reload the config\n")
        while not runnable:
            usrin = input(">")
            usrin = usrin.replace(" ","").casefold()

            if usrin == "config":
                print("\nOpening config file...\n")
                os.startfile(f"{app_dir}\\config.cfg")
            elif usrin == "regenerate":
                print("\nRenegerating config file...")
                os.remove(f"{app_dir}\\config.cfg")
                generateConfig()
            elif usrin == "recreate":
                print("\nRecreating backups folder...")
                if makeBackupFolder() == 0:
                    print("Successfully recreated backups folder\n")
            elif usrin == "reload":
                loadConfig()
                verifyConfig()
                if not runnable:
                    print("\nUnable to verify config file")
                    print("Try editing config file again or regenerating config file\n")
                else:
                    os.system("cls")
            else:
                print("\nInvalid input\n")

#Initializes the config and backup folder for use
def init():
    global runnable

    if makeAppDir() == 0:
        #Generate config file if it doesn't already exist
        if not os.path.isfile(f"{app_dir}\\config.cfg"):
            generateConfig()
        loadConfig()
        verifyConfig()

        #If making a backup folder fails, then prevent the app from running
        if not makeBackupFolder() == 0:
            runnable = False
    else:
        print("Unable to make the app directory in the user folder. Exiting...")
        time.sleep(3)
        sys.exit()
        
#Prints a welcome text
def printHello():
    print("Minecraft Save Backup Application")
    print(f"Author: abacuscl; {VERSION}\n")

#Creates the application directory
def makeAppDir():
    global app_dir
    
    if verifyLocation(f"{Path.home()}"):
        try:
            os.mkdir(f"{Path.home()}\\MCWorldBackup")
            app_dir = f"{Path.home()}\\MCWorldBackup"
            return 0
        except FileExistsError:
            app_dir = f"{Path.home()}\\MCWorldBackup"
            return 0
        except Exception as e:
            with open("error.log", "a") as f:
                f.write(f"Error occurred in method makeAppDir():\n{e}\n\n")
            return 1
    else:
        return 1

#Creates and populates the config file with default values
def generateConfig():
    with open(f"{app_dir}\\config.cfg", "w") as f:
        f.write("Minecraft Save Directory\n")
        f.write(f"{DEFAULT_SAVEDIR}\n\n")
        f.write("Backup To Directory\n")
        f.write(f"{DEFAULT_BACKUPDIR}\n\n")
        f.write("Backup Frequency (minutes)\n")
        f.write(f"{DEFAULT_FREQ}\n\n")
        f.write("Versions To Keep (across all saves)\n")
        f.write(f"{DEFAULT_KEPT}")
    if runnable == False:
        print("Config file successfully regenerated\n")

#Loads the settings from the config file into variables
def loadConfig():
    global save_dir
    global backup_dir
    global backup_freq
    global ver_kept
    global runnable

    with open(f"{app_dir}\\config.cfg") as f:
        count = 1

        #Run through the entire file
        for line in f:
            line = line.strip()

            #If the line is blank, skip it
            if line == "":
                count += 1

            #If the line is even then process it for data
            elif count % 2 == 0:

                #If it is line 2, then save the line as the save directory
                if count == 2:

                    #Verification of the file path occurs first, if it fails the program will not run
                    if verifyLocation(line):
                        save_dir = line

                    #If the user set location is invalid, attempt to fall back on the default directory
                    elif verifyLocation(DEFAULT_SAVEDIR):
                        save_dir = DEFAULT_SAVEDIR
                    else:
                        runnable = False

                #If it is line 4, then save the line as the backup directory
                elif count == 4:

                    #Verification of the file path occurs first, if it fails the program will not run
                    if verifyLocation(line):
                        backup_dir = line

                    #If the save directory can be validated, then put the folder there
                    elif verifyLocation(save_dir):
                        backup_dir = f"{save_dir}\\backups"
                        if not makeBackupFolder() == 0:
                            runnable = False
                    
                    #If the user set location is invalid, attempt to fall back on the default directory
                    elif verifyLocation(DEFAULT_SAVEDIR):
                        backup_dir = DEFAULT_BACKUPDIR
                    else:
                        runnable = False

                #If it is line 6, then attempt to cast the line as a float, convert to seconds, and save as backup frequency
                #If it fails, then nothing happens and the error log is appended
                elif count == 6:
                    try:
                        backup_freq = (float(line) * 60)
                    except Exception as e:
                        with open("error.log", "a") as f:
                            f.write(f"Error occurred in method loadConfig():\n{e}\n\n")

                #If it is line 8, then attempt to cast the line as an integer and save as the kept versions
                elif count == 8:
                    try:
                        ver_kept = int(line)
                    except Exception as e:
                        with open("error.log", "a") as f:
                            f.write(f"Error occurred in method loadConfig():\n{e}\n\n")

            #If all else fails, then skip the line
            else:
                count += 1

#Verifies that all the necessary variables were read from the config file
def verifyConfig():
    global runnable

    #If any of the values are empty or are a preset default value, then don't run the program
    #Otherwise, it is error free and enable running
    if save_dir == "":
        runnable = False
    elif backup_dir == "":
        runnable = False
    elif backup_freq == -1 or backup_freq < 0:
        runnable = False
    elif ver_kept == -1 or ver_kept < 0:
        runnable = False
    else:
        runnable = True

#Makes the backup directory based on the backup directory
def makeBackupFolder():
    try:
        #If there is no specified directory, revert to default
        if backup_dir == "":
            os.mkdir(DEFAULT_BACKUPDIR)
        else:
            os.mkdir(backup_dir)
        return 0

    #Ignore that the folder already exists
    except FileExistsError:
        return 0
    except Exception as e:
        print("Could not make the backup folder:")
        print(e)
        with open("error.log", "a") as f:
            f.write(f"Error occurred in method makeBackupFolder():\n{e}\n\n")
        return 1

#Verifies the location of a file path by reading/writing to a test file and then deleting it
def verifyLocation(location):
    try:
        with open(f"{location}\\test.file", "w") as f:
            f.write("test\ntest2")
        with open(f"{location}\\test.file", "r") as f:
            string = f.read()
        os.remove(f"{location}\\test.file")
        return True
    except:
        return False

'''
Input Methods
'''
#Gets the current mode of the program
def getMode():
    while True:
        print("Enter the mode:\n")
        print("[1] Copy Save")
        print("[2] One Time Backup")
        print("[3] Auto Backup\n")
        usrin = input(">")
        usrin = usrin.replace(" ", "").casefold()

        if isValidCommand(usrin):
            executeCommand(usrin)
        elif usrin == "1":
            return 1
        elif usrin == "2":
            return 2
        elif usrin == "3":
            return 3
        else:
            print("\nInvalid mode selection\n\n")

#Asks the user to select a current save file to copy/back up
def selectSave():
    global selected_world
    
    while True:
        #List the current folders in the save directory and remove the backups folder from the list
        ls = os.listdir(save_dir)
        ls.remove("backups")
        
        count = 1
        print("\nSelect a save file:\n")
        for i in ls:
            print(f"[{count}] {i}")
            count += 1

        print("")
        usrin = input(">")
        usrin = usrin.replace(" ", "")
        if isValidCommand(usrin):
            executeCommand(usrin)
            break
        else:
            try:
                selected_world = ls[int(usrin) - 1]
                break
            except:
                print("\nInvalid selection\n")

'''
Functionality Methods
'''
#Copies a save from the save directory to a user specified path
def copySave():
    global current_mode

    selectSave()
    if not current_mode == 0:
        while True:
            print("\nFull path to copy the save file to:\n")
            usrin = input(">")

            if isValidCommand(usrin):
                executeCommand(usrin)
                break
            elif verifyLocation(usrin):
                copyWorldFiles(usrin, "null")
                time.sleep(3)
                resetCLI()
                break
            else:
                print("\nInvalid path\n")

#Copies the world directory to the argument dest       
def copyWorldFiles(dest, typ):
    if typ == "backup":
        print(f"\nBacking up save file \"{selected_world}\"...")
    else:
        print(f"\nCopying save file \"{selected_world}\"...")

    #Format the copied folder with the date and time it was copied
    curtime = datetime.datetime.now()
    strtime = curtime.strftime("%m-%d-%Y %H.%M.%S")
    src = f"{save_dir}\\{selected_world}"
    dest = f"{dest}\\{selected_world} {strtime}"

    try:
        #If it's a backup, check if there are more than the amount of kept versions allowed
        if typ == "backup":
            ls = os.listdir(backup_dir)

            #If there are more backups than allowed, attempt to delete the oldest one
            if len(ls) >= ver_kept:
                try:
                    temp = ls[0]
                    shutil.rmtree(f"{backup_dir}\\{ls[0]}")
                    print(f"Old backup version: \"{temp}\" deleted successfully")
                except Exception as e:
                    print("\nCould not delete the old backup version:")
                    print(e)
                    with open("error.log", "a") as f:
                        f.write(f"Error occurred in method copyWorldFiles():\n{e}\n\n")

        #Attempt to copy the folder from the source path to the destination path
        try:
            shutil.copytree(src, dest)
            if typ == "backup":
                print("Successfully backed up the save file")
            else:
                print("Successfully copied the save file")
        except IOError as pe:
            if "session.lock" in f"{pe}":
                if typ == "backup":
                    print("Successfully backed up the save file, however session.lock is empty")
                else:
                    print("Successfully copied the save file, however session.lock is empty")
            else:
                if typ == "backup":
                    print("\nCould not backup the save file:")
                    print(pe)
                else:
                    print("\nCould not copy the save file:")
                    print(pe)
                with open("error.log", "a") as f:
                    f.write(f"Error occurred in method copyWorldFiles():\n{pe}\n\n")
        except Exception as e:
            if typ == "backup":
                print("\nCould not backup the save file:")
                print(e)
            else:
                print("\nCould not copy the save file:")
                print(e)
            with open("error.log", "a") as f:
                f.write(f"Error occurred in method copyWorldFiles():\n{e}\n\n")

    #Used only for autosaving;
    #If the directory becomes unavailable, then halt autosave and disable running the program
    except:
        global runnable
        global quit_autosave
        
        runnable = False
        print("\n\nCould not access backup directory, Aborting backup...\n")
        print("Type back to return to the main menu")
        quit_autosave()

#Backs up the save to the backup folder and creates the folder if it does not already exist
def backupSave():
    if makeBackupFolder() == 0:
        selectSave()
        
        if not current_mode == 0:
            copyWorldFiles(backup_dir, "backup")
            time.sleep(3)
            resetCLI()
    else:
        time.sleep(3)
        resetCLI()

#Automatically backs up the specified save file 
def autoBackupSave():
    global quit_autosave
    global runnable
    
    if makeBackupFolder() == 0:
        selectSave()
        if not current_mode == 0:
            os.system("cls")
            printHello()
            print("AUTOSAVE MODE\n")
            print("Leave the window open and running in the background")
            print("The autosave interval can be adjusted in the config file\n")
            print("Type back to exit autosave or quit to exit the app\n")

            #Start the autosave process on a new thread
            quit_autosave = doAutosave(backup_freq)

            #Get command inputs if the user would like to go back
            while True:
                usrin = input("")
                usrin = usrin.replace(" ", "").casefold()
                
                #If the command is back, then halt autosaving and return to the main menu
                if usrin == "back":
                    quit_autosave()
                    if runnable == True:
                        print("\nAuto backup shut down successfully...")
                        time.sleep(3)
                    resetCLI()
                    break

                #If the command is quit, then stop the autosave and quit the application
                elif usrin == "quit":
                    quit_autosave()
                    if runnable == True:
                        print("\nAuto backup shut down successfully...")
                    time.sleep(3)
                    sys.exit()
    else:
        time.sleep(3)
        resetCLI()

#Autosaving process thread
def doAutosave(interval):
    global runnable
    stopped = Event()
    def loop():

        #While not stopped over the specified time interval, save the file
        while not stopped.wait(interval):
            copyWorldFiles(backup_dir, "backup")
            curtime = datetime.datetime.now()
            time = curtime.strftime("%m-%d-%Y %H.%M.%S")
            if runnable == True:
                print(f"Backup successfully completed on {time}\n")
    Thread(target=loop).start()
    return stopped.set    

'''
Command Methods
'''
#Resets the CIO to the main menu
def resetCLI():
    global current_mode
    
    os.system("cls")
    current_mode = 0
    printHello()

#Checks if the user's input is a valid command
def isValidCommand(command):
    if command == "quit":
        return True
    elif command == "back" and not current_mode == 0:
        return True
    elif command == "config":
        return True
    else:
        return False

#Executes the user's inputted command
def executeCommand(command):
    if command == "quit":
        sys.exit()
    elif command == "back" and not current_mode == 0:
        current_mode == 0
        resetCLI()
    elif command == "config" and current_mode == 0:
        print("\nOpening config file...")
        openConfig()
    elif command == "config":
        print("\nCannot open config when executing copies")

#Opens the config file, works only on Windows   
def openConfig():
    os.startfile(f"{app_dir}\\config.cfg")
    print("\nApp must be restarted for changes to take effect\n")

'''
Start the Application
'''
if __name__ == "__main__":
    run()
