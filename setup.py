#!/usr/bin/python
# Script Name: setup.py
# Script Function:
#	This script will install pharos remote printing on the system.
#	The following tasks will be performed:
#	1. Install the pharos backend to cups backend directory
#	2. Install the popup scripts to /usr/local/bin/pharospopup
#	3. Install the config file to /usr/local/etc/
#	4. Install the uninstall script to /usr/local/bin/uninstall-pharos
#	5. Setup the users desktop environment to autorun the pharospoup at login
#	6. Create the print queues as defined in printers.conf
#	
# Usage: 
#	$sudo python setup.py
#		This will install pharos remote printing
#
# Author: Junaid Ali
# Version: 1.0

# Imports ===============================
import os
import sys
import logging
import subprocess
import re
import shutil

# Script Variables ======================
logFile = os.path.join(os.getcwd(), 'pharos-linux.log')
pharosBackendFileName = 'pharos'
pharosPopupServerFileName = 'pharospopup'
pharosConfigFileName = 'pharos.conf'
printersConfigFile = os.path.join(os.getcwd(), 'printers.conf')

popupServerInstallDIR = '/usr/local/bin'
pharosConfigInstallDIR = '/usr/local/etc'

# Regular Expressions
gnomeWindowManagerRegularExpression = 'gnome|unity'
kdeWindowManagerRegularExpression = 'kde'

# Functions =============================
def checkProcess(processName):
	"""
	Checks if the given process is running
	"""
	logger.info('Checking if %s is running' %processName)
	logger.info('Getting list of processes')
	try:
		ps = subprocess.check_output(['ps', 'ax'])
	except CalledProcessError as (errCode, errMessage):
		logger.error('Could not get list of running processes')	
		logger.error('Error: %s Message: %s' %(errCode, errMessage))
		return False
		
	processes = ps.split('\n')
	processFound = False
	for process in processes:
		if re.search(processName, process):
			logger.info('%s is running with details: %s ' %(processName, process))
			processFound = True
			break			
		else:
			logger.info('Process %s is not %s' %(process, processName))
	if processFound:
		logger.info('%s is running.' %processName)
		return True
	else:
		logger.error('%s is not running.' %processName)
		return False
		
		
def checkPreReqs():
	"""
	Verifies if all program pre-requisites are satisfied. If not then exit the program
	"""
	logger.info('Verifying pre-requisites')
	
	# Check if CUPS is running
	logger.info('checking if cups is available')
	if checkProcess('cups'):
		logger.info('CUPS is installed and running. Can continue')
	else:
		logger.error('CUPS is either not installed or not running. Please make sure CUPS is installed and running before proceeding')
		sys.exit(1)
	
	# Check wxPython	
	logger.info('checking if wxPython is available')
	try:
		import wxPython
	except:
		logger.error('wxPython is not installed. Please make sure wxPython is installed before proceeding')
		sys.exit(1)
	logger.info('wxPython is installed')
	
def installBackend():
	"""
	Install the pharos backend
	"""
	backendDIR = '/usr/lib/cups/backend'
	backendFile = os.path.join(os.getcwd(), pharosBackendFileName)
	
	logger.info('Checking for CUPS backend directory %s' %backendDIR)
	if os.path.exists(backendDIR):
		logger.info('CUPS backend directory %s exists' %backendDIR)
	else:
		logger.error('CUPS backend directory %s not found. Make sure CUPS is correctly setup before proceeding.' %backendDIR)
		sys.exit(1)
	
	logger.info('Copy backend file %s to %s' %(backendFile, backendDIR))
	try:
		shutil.copy(backendFile, backendDIR)
	except IOError as (errCode, errMessage):
		logger.error('Could not copy file %s to %s' %(backendFile, backendDIR))	
		logger.error('Error: %s Message: %s' %(errCode, errMessage))
		sys.exit(1)
	
	if os.path.exists(os.path.join(backendDIR, backendFile)):
		logger.info('Backend file copied successfully')
	else:
		logger.error('Could not copy file %s to %s' %(backendFile, backendDIR))
		sys.exit(1)
	
	# Set execution bits for backend files
	logger.info('Set execution bit on the backend files')
	try:
		chmod = subprocess.check_output(['chmod', '755', os.path.join(backendDIR, pharosBackendFileName), os.path.join(backendDIR, 'lpd')])
	except subprocess.CalledProcessError:
		logger.error('Could not change the execution bit on backend files: %s, %s' %(os.path.join(backendDIR, pharosBackendFileName), os.path.join(backendDIR, 'lpd')))		
		sys.exit(1)
	logger.info('Successfully setup the execution bit on backend files: %s, %s' %(os.path.join(backendDIR, pharosBackendFileName), os.path.join(backendDIR, 'lpd')))

def installPopupServer():
	"""
	Installs the popup server files
	"""
	logger.info('Installing poup server files')
	popupExecutable = os.path.join(os.getcwd(), pharosPopupServerFileName)
	pharosConfig = os.path.join(os.getcwd(),pharosConfigFileName)
	 
	try:
		logger.info('Trying to copy %s to %s' %(popupExecutable, popupServerInstallDIR))
		shutil.copy(popupExecutable, popupServerInstallDIR)
		logger.info('Successfully copied %s to %s' %(popupExecutable, popupServerInstallDIR))		
	except IOError as (errCode, errMessage):
		logger.error('Could not copy file %s to %s' %(pharosConfig, pharosConfigInstallDIR))
		logger.error('Error: %s Message: %s' %(errCode, errMessage))
		sys.exit(1)
	
	try:
		logger.info('Trying to copy %s to %s' %(pharosConfig, pharosConfigInstallDIR))
		shutil.copy(pharosConfig, pharosConfigInstallDIR)
		logger.info('Successfully copied %s to %s' %(pharosConfig, pharosConfigInstallDIR))
	except IOError as (errCode, errMessage):
		logger.error('Could not copy file %s to %s' %(pharosConfig, pharosConfigInstallDIR))
		logger.error('Error: %s Message: %s' %(errCode, errMessage))
		sys.exit(1)
	
def addPopupServerToGnomeSession():
	"""
	Adds the popup server to gnome session
	"""
	gnomeAutoStartFile = """
[Desktop Entry]
Type=Application
Exec=%s
Hidden=false
X-GNOME-Autostart-enabled=true
Name[en_US]=PharosPopup
Name=PharosPopup
Comment[en_US]=Pharos Popup Server
Comment=Pharos Popup Server
""" %(os.path.join(popupServerInstallDIR, pharosPopupServerFileName))
	
	logger.info('Getting list of current users')
	currentUsers = os.listdir('/home')	
	for user in currentUsers:
		logger.info('Adding autostart file to user %s' %user)
		autoStartDIR = os.path.join('/home', user, '.config', 'autostart')
		logger.info('Checking if directory %s exists' %autoStartDIR)
		if not os.path.exists(autoStartDIR):
			logger.info('Creating autostart directory %s' %autoStartDIR)
			os.makedirs(autoStartDIR)			
		else:
			logger.info('Autostart directory %s already exists' %autoStartDIR)
		
		if os.path.exists(autoStartDIR):			
			autoStartFile = os.path.join('/home', user, '.config', 'autostart', 'pharospopup.desktop')
			# Delete old file if it exists
			if os.path.exists(autoStartFile):
				logger.info('Deleted old version of autostart file: %s' %autoStartFile)
				os.remove(autoStartFile)
			# create new file
			autoStartFH = open(autoStartFile, 'w')
			autoStartFH.write(gnomeAutoStartFile)
			autoStartFH.close()
			logger.info('Successfully added autostart for %s user' %user)
		else:
			logger.warn('Autostart file %s could not be created' %autoStartFile)
	
	# Update the autostart file for root
	logger.info('Updating autostart file for root')
	rootAutoStartDIR =  os.path.join('/root', '.config', 'autostart')
	rootAutoStartFile = os.path.join('/root', '.config', 'autostart', 'pharospopup.desktop')
	if not os.path.exists(rootAutoStartDIR):
		logger.info('Creating autostart directory %s' %rootAutoStartDIR)
		os.makedirs(rootAutoStartDIR)
	if os.path.exists(rootAutoStartFile):
		logger.info('Deleting old version of skel autostart file: %s' %rootAutoStartFile)
		os.remove(rootAutoStartFile)
		
	rootAutoStartFH = open(rootAutoStartFile, 'w')
	rootAutoStartFH.write(gnomeAutoStartFile)
	rootAutoStartFH.close()
	logger.info('Successfully added autostart to root user')
		
	# Update the autostart file in skel
	logger.info('Updating autostart file for future users')
	skelAutoStartDIR = os.path.join('/etc/', 'skel', '.config', 'autostart')
	skelAutoStartFile = os.path.join('/etc/', 'skel', '.config', 'autostart', 'pharospopup.desktop')
	
	if not os.path.exists(skelAutoStartDIR):
		logger.info('Creating autostart directory %s' %skelAutoStartDIR)
		os.makedirs(skelAutoStartDIR)
	
	if os.path.exists(skelAutoStartFile):
		logger.info('Deleting old version of skel autostart file: %s' %skelAutoStartFile)
		os.remove(skelAutoStartFile)
		
	skelAutoStartFH = open(skelAutoStartFile, 'w')
	skelAutoStartFH.write(gnomeAutoStartFile)
	skelAutoStartFH.close()
	logger.info('Successfully added autostart in skel for future users')

def addPopupServerToKDESession():
	"""
	Adds autostart option for KDE desktops
	"""
	logger.error('addPopupServerToKDESession() not implemented')
	
def addPopupServerToLogin():
	""""
	Add the popup server to all users.
	Add the popup server for all future users
	"""	
	logger.info('Analyzing desktop environment')
	if checkProcess('gnome'):
		logger.info('User is using gnome window manager')
		addPopupServerToGnomeSession()
	elif checkProcess('kde'):
		logger.info('User is using kde Window Manager')
		addPopupServerToKDESession()
	else:
		logger.warn('Users window manager is not recognized. Could not setup login scripts for popupserver. Please use your window manager to add startup script %s' %os.path.join(os.getcwd(),pharosPopupServerFileName))
	logger.info('Completed adding pharos popup server to login')

def installPrintQueues():
	"""
	Installs print queues based on the printers.conf file
	"""
	logger.info('Installing print queues')
	
def setupLoggingDirectories():
	"""
	Setup the permissions for log folders
	""""
	logger.info('Creating log directories')
	
def main():
	"""
	The main installer script
	"""
	logger.info('Beginning %s' %sys.argv[0])
	
	# check prerequisites
	checkPreReqs()
	
	# Install backend
	installBackend()
	
	# Install popup server files
	installPopupServer()
	
	# Setup Popup server to run at login
	addPopupServerToLogin()
	
	# Setup Print Queues
	installPrintQueues()
	
	# Setup Log Directories
	setupLoggingDirectories()
	
	

# Main Script ============================

# Create logger
logger = logging.getLogger('pharos-linux-setup')
logger.setLevel(logging.DEBUG)
# Create file handler
fh = logging.FileHandler(logFile)
fh.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add loggers
logger.addHandler(fh)
logger.addHandler(ch)

if __name__ == "__main__":
	main()
