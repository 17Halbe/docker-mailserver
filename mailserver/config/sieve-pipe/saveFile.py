#!/usr/bin/env python3
import sys
import os, getopt
import logging
import traceback
import getpass
from logging.handlers import SysLogHandler

mmsg = ""
user = os.environ["RECIPIENT"]
dest_Path = os.path.join("/mnt/btsync/mail-attachments/",user)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

syslog = SysLogHandler(address='/dev/log',facility='mail')
formatter = logging.Formatter('%(asctime)s saveFile(' + getpass.getuser() + '): %(levelname)-8s %(message)s', datefmt='%b %d %H:%M:%S')

syslog.setFormatter(formatter)
logger.addHandler(syslog)

#logging.basicConfig(format='%(asctime)-11s gar-nich saveFile(' + getpass.getuser() + '): %(levelname)-8s %(message)s', filename='/var/log/mail.log', datefmt='%b %d %H:%M:%S',level=logging.DEBUG)
logging.debug("starting up as user " + getpass.getuser())
def log_error(e, e_text="Error: ", exit_code=-1 ):
	logging.error(e_text + str(sys.exc_info()[0]) + "\n" + str(sys.exc_info()[1]) + "\n" + str(sys.exc_info()[2]) + "\n" + str(e))
	if exit_code > -1:
		sys.exit(exit_code)

def safe_rename(source,destination, chmode):
	if os.path.exists(destination):
		destDir = os.path.dirname(destination) + "/"
		destFile = os.path.splitext(os.path.basename(destination))
		i = 1		
		while os.path.exists(os.path.join(destDir, destFile[0] + "_" + str(i) + destFile[1])):
			i += 1
		destination = os.path.join(destDir, destFile[0] + "_" +  str(i) + destFile[1])
	try:
		os.rename(source, destination)
		os.chmod(destination,chmode)
		return destination
	except:
		log_error(traceback.format_exc(),"Couldn't move " + source + " -> " + destination)
		return ""

try:
	opts, args = getopt.getopt(sys.argv[1:],"u:")
except getopt.GetoptError:
	log_error(traceback.format_exc(),"No User found",2)
'''
for opt, arg in opts:
	if opt == ('-u'):
		user = arg

if "alex" in user:
	dest_Path += "alex"
elif "bine" in user:
	dest_Path += "bine"
else:
	logging.warning("No User found. Username provided doesn't have a corresponding Destination Path.")
	sys.exit(2)
'''

logging.debug("Processing Mail for User " + user)
for line in sys.stdin:
	#mail.write(line)
	mmsg += line

from subprocess import Popen, PIPE, STDOUT
#p = Popen(['/usr/bin/munpack -q -f -C /tmp/'], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
p = Popen(['/usr/bin/ripmime -i - -d /tmp/ --no-nameless --overwrite --prefix attachment -v'], stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True)
#Sample Output:
#Decoding filename=17RS05528129.pdf
#Removed ./textfile1 [status = 0]
#Removed ./textfile0 [status = 0]

stdout_data = p.communicate(input = mmsg.encode('utf8'))
#print ("0:")
mfiles = stdout_data[0].decode('utf8').split("\n")
logging.debug("Mail-Files: " + str(mfiles))
for mfile in mfiles:
	if ".pdf" in mfile:
		mfile = mfile.split('filename=')[1]
		logging.info("Processing " + mfile)
		#mfile = mfile.split(" ")
		safe_rename(os.path.join("/tmp", mfile[0]), os.path.join(dest_Path, "attachment " + mfile), 0o664)
	
