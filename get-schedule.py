#!/usr/bin/env python


# Python script to connect to MediaPortal server and create a list of all upcoming scheduled recordings 
# This list can be used to power on the Mediaportal server using Wake on LAN (WOL)

import MySQLdb
import datetime
import os
import ConfigParser


#Check if MP server is online
def online (hostname):
	response = os.system("ping -c 1 " + hostname)
	return response

#Get program details from MP database	
def searchForProgram (searchQuery):
	curProgram.execute(searchQuery)
	print (searchQuery)
	prg = ""
	for item in curProgram.fetchall():
		prg = prg + str(item[2]) + "\t" + str(item[3]) + "\t" +  item[4] + "\n"
	return prg
	
#Convert start time	to string
def getTheStartTime (DT):
	return datetime.datetime.strptime(DT, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S')

#Convert start day to string	
def getTheStartDay (DT):	
	daynum = datetime.datetime.strptime(DT, '%Y-%m-%d %H:%M:%S').strftime('%w')
	daynum = int(daynum) + 1
	return str(daynum)


	
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

hostname = config.get('config', 'mp_server')
sqlUsr = config.get('config', 'sql_user')
sqlPW = config.get('config', 'sql_password')
sqlDB = config.get('config', 'sql_database')
dataFile = config.get('config', 'db_file')


# Check MP server is online	
#if not online(hostname) == 0:
#	quit()



# Setup connection to MP MySQL Database
try:
	db = MySQLdb.connect(host=hostname, 
                     user=sqlUsr, 
                     passwd=sqlPW,
                     db=sqlDB)
except:
	print "Unable to connect to MP SQL Server"
	quit()

# Open file for output
f = open(dataFile, 'w')	

# Create Cursor objects to execute SQL queries
cur = db.cursor()
curProgram = db.cursor()

# Execute SQL query to get all data from 'schedule' database
cur.execute("SELECT * FROM schedule")

# print all the first cell of all the rows
for row in cur.fetchall() :
	
	schIdChannel=str(row[1])
	schScheduleType=row[2]
	schProgramName=row[3]
	schStartTime=str(row[4])
	schEndTime=str(row[5])
	n=schScheduleType
	
	theStartTime = getTheStartTime(schStartTime)
	theStartDay = getTheStartDay(schStartTime)
	
	print str(schScheduleType), schProgramName, schStartTime
	f.write (schStartTime + "\t" + schEndTime + "\t" + schProgramName + " * \n")
	
	#0 = Record Once (1)
	#Query: Where title and channel and startdate and starttime
	if n == 0:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and idChannel = \"" + schIdChannel + "\" and startTime = \"" + schStartTime + "\"")
		print s
		f.write (s)
	
	#Record Every Day at this time (5)
	#Query: Where title and starttime
	elif n == 1:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and Time(startTime) = \"" + theStartTime + "\"")
		print s
		f.write (s)
		
	#Record every Week at this time (4) 	
	#Query: Where title and startTime and Day of Week
	elif n == 2:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and Time(startTime) = \"" + theStartTime + "\" and DAYOFWEEK(starttime) = \"" + theStartDay + "\"")
		print s
		f.write (s)
		
	#Record Every Time on this channel (2)
	#Query: Where title and channel
	elif n == 3:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and idChannel = \"" + schIdChannel + "\"")
		print s
		f.write (s)
		
	#Record Every Time on Every Channel (3)
	#Query: Where title
	elif n == 4: 
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\"")
		print s
		f.write (s)
		
	#Record Weekends (7)
	#Query: Where title and dayofweek is saturday(7) or sunday(1)
	elif n == 5:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and (DAYOFWEEK(starttime) = 1 or DAYOFWEEK(starttime) = 7)")
		print s
		f.write (s)
		
	#Record Weekdays (6) 
	#Query: Where title and dayofweek is between Monday and Friday
	elif n == 6:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and DAYOFWEEK(starttime) between 2 and 6")
		print s
		f.write (s)
	
	#Weekly on this channel (8)
	#Query: Where title and channel and starttime and dayofweek
	elif n == 7:
		s = searchForProgram("SELECT * FROM program WHERE title = \"" + schProgramName + "\" and idChannel = \"" + schIdChannel + "\" and Time(startTime) = \"" + theStartTime + "\" and DAYOFWEEK(starttime) = \"" + theStartDay + "\"")
		print s
		f.write (s)
		
	print ("")	
		
# Script complete		
db.close()
f.close()
quit()
