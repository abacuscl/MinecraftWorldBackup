 # MinecraftWorldBackup
 A simple command line application to back up your minecraft worlds without mods.
 *Version 0.1*
 **Currently Windows Only**

 ----
 ## Table of Contents
 -[Features](#features)
 -[Technologies](#technologies)
 -[Setup](#setup)
 -[Usage](#usage)
 -[Ideas to Implement](#ideas-to-implement)
 
 ----
 ## Features
 - One time world copy
 - One time world backup
 - Interval backup
 - Editable config file
 - Command Line Interface
 
 ### Commands
 - config
   - Opens the configuration file to change settings.
   - Can only be used on the first mode selection menu.
 
 - back
   - Returns to the mode select menu.
   
 - quit
   - Quits and closes the app.
 
 ----
 ## Technologies
 Created with:
 - Python version 3.8.7
 
 ----
 ## Setup
 To use this application, you need [Python](https://www.python.org/downloads/) version 3.8+ 
 and [Git](https://git-scm.com/downloads) if you intend to clone using the command line.
 
 Using Git:
 '''
 git clone link
 
 cd minecraftworldbackup
 
 python WorldBackupAndCopy.py
 '''
 
 Cloning from web browser:
 
 1. Clone the repository as a .zip file
 
 2. Unzip the file in the desired directory
 
 3. Open the file and double click on WorldBackupAndCopy.py
 
 ----
 ## Usage
 
 ### Using the App
 The command line interface is simple and easy to follow. The commands are listed [here.](#commands)
 The copy feature copies a world to a specified path. The backup feature copies a world to the
 backups folder and the auto backup feature copies a world to the backups world at an interval set in the
 config file.
 
 ### Changing Settings
 By typing config on the select mode menu, the config.cfg file will open in your default text editor.
 The settings to change are:
 
 - Minecraft Save Directory
   - Path to the minecraft save directory.
 
 - Backup To Directory
   - Directory to backup world files to.

 - Backup Frequency
   - Measured in minutes.
   - The frequency that the auto backup mode will run.

 - Versions to Keep
   - The total number of backups to keep.
 
 ### IMPORTANT:
 - When backing up files while Minecraft is running, you may see a message saying session.lock is empty.
   - This is normal, and it does not affect the world file
   
 - [Optifine](https://optifine.net/downloads) is recommended if you plan to adjust the backup frequency
   - By default, Minecraft does not allow you to adjust the autosave interval.
   - The default Minecraft backup interval is five minutes.
   - If you adjust the backup interval to less than five minutes, your world file may be outdated regardless of the timestamp on the folder. 
   - The Minecraft save interval and the backup frequency should be equal.
 
 ----
 ## Bug Report
 To open a bug report or feature request, create an issue on the repository page.
 
 ----
 ## Ideas to Implement
 - [] Export errors to an error.log file to make bugfixes easier
 - [] Make the python files into an executable