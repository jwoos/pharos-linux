# Pharos Linux
This program provides a linux equivalent of the Pharos Remote Printing Package available for Windows and Macintosh clients. This package will install a new CUPS backend that will allow printing to lpd queues on the pharos uniprint print server. Also it will install a new pharos popup server that will allow for users to input their printing ID's to be tied with the print jobs they send. This will allow the users to use their printing ID's to release the print jobs at the pharos release stations.

## PRE-REQUISITES
1. CUPS printing system
	- Most linux distributions use CUPS printing by default. To check if CUPS is running open a web browser and go to http://localhost:631
	- This should launch the CUPS printing interface.

2. wxPython library
	- This python library is required to display popups used for printing to pharos printing queues.
	- Check if wxpython is installed
		1. Open terminal
		2. Run python interactive shell `python2`
		3. Try to import the wxpython module `import wx`

3. Printer Drivers
	- Your desktop should have all the required drivers that are mentioned in the printers.conf file. If the printer driver defined in the configuration file is not found then that printer will not be installed. The printers.conf file is located in the same directory as this README file.

On systems with selinux enabled (Red Hat and derivatives). you will need to disable selinux or setup policies in order for the popup application to work correctly. Please refer to the corresponding systems administration guide to disable selinux.

## Installation
Make sure you have the following pre-requisites installed before proceeding with the installation.

To install pharos remote printing open terminal and go to this package directory. Run the setup.py file as administrator user

```
sudo python2 setup.py
```

You will be presented with an EULA (if present) and if you accept it the installation will continue.

### Automatically Start Popup Server
Place pharos-server.service in `/etc/systemd/system/`, then run `systemctl enable pharos-server.service`

## Uninstalling
The installer will add an uninstallation program to `/usr/local/bin/pharos-uninstall`

```
sudo python2 /usr/local/bin/pharos-uninstall
```
