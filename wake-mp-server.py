#!/usr/bin/env python

import datetime
import os
import socket
import ConfigParser
import fcntl
import struct

# Globals
LEAD_TIME = 10

# Convert time from a string to datetime format
def convertTime(strTime):
	return datetime.datetime.strptime(strTime, "%Y-%m-%d %H:%M:%S")

	
# Check if time now is greater than start time and less than end time
def compareTime(start, end, now):
	CT = False
	if ((now >= start) and (now < end)):
		CT = True
	return CT

	
# Subtract 10 minutes from the start time	
def subtractTime(T):
	##T = datetime.datetime.strptime(T, "%Y-%m-%d %H:%M:%S")
	T = T - datetime.timedelta(minutes = LEAD_TIME)
	return T

	
# If on then send wake on lan packet and quit
def powerOn(MAC, bIP):
	os.system("wakeonlan -i " + bIP + " " + MAC)

# Add entry	to log file
def logAction(eventstr):
	log.write (str(nowTime) + ": " + eventstr + "\n")

# Calculate broadcast addresses of local networks (for WOL)	
def get_broadcast_address(ip):
	tmp = str(ip).split('.')
	return tmp[0] + "." + tmp[1] + "." + tmp[2] + ".255"
	 

def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(
		s.fileno(),
		0x8915,  # SIOCGIFADDR
		struct.pack('256s', ifname[:15])
	)[20:24])
	
	
	
# Main

# Check config file exists	

dir = os.path.dirname(os.path.abspath(__file__))
filepath = dir + '/mpw.conf'

if not os.path.isfile(filepath):
	print ("Error - Missing Config File: mpw.conf")
	quit()

# Get config	
config = ConfigParser.ConfigParser()
config.read(filepath)

htpcMAC = config.get('config', 'mp_server_mac')	
dataFile = config.get('config', 'db_file')
logFile = config.get('config', 'wmps_logfile')


# Get broadcast addresses of local networks (for WOL)
broadcastIP = get_broadcast_address(get_ip_address('eth0'))
	
# Open file containing scheduling data for recording
file = open(dataFile, 'r')

# Open log file
log = open(logFile, 'a+')

# Get the current time
nowTime = datetime.datetime.now()

logAction ("Checking schedule")

# loop through each line in the data file
for line in file:

	tokens = line.split("\t")
	
	# Get program start time (-10 minutes)
	startTime = convertTime(tokens[0])
	startTime = subtractTime(startTime)
	
	# Get program end time
	endTime = convertTime(tokens[1])
	
	# If a program that is scheduled to record is currently on, send WOL packet
	if compareTime(startTime, endTime, nowTime):
		print "Its On! - " + tokens[2]
		logAction (str(nowTime) + ": " + tokens[2])
		powerOn(htpcMAC, broadcastIP)
		

file.close()
log.close()
		
