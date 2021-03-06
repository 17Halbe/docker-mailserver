#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# mail-attachments-archiver
# Author: Alexader Stölting
# 

# libraries import
import email, email.header, smtplib, os, re, time, sys, subprocess
from email.mime.text import MIMEText
from email.parser import Parser
from smtplib import SMTP
#from email.Header import Header
from email.utils import parseaddr, formataddr
import urllib
import logging
from logging.handlers import SysLogHandler
import base64
import hashlib
import datetime

### Adjust to your needs:
#t[t.find("."):]
try: 
	host=os.environ["HOST"]
except:
	host="mail.localhost"

outputdir="/var/attachments"  						# local Location to save the attachments to. Has to be writable by user: docker 
nginx_url = "https://downloads" + host[host.find("."):]
try:
   nginx_url = "https://downloads." +  os.environ["NGINX_DOWNLOAD_DOMAIN"]			#the download url 
except:
   pass

nginx_secret = "<MYSECRET>" #os.environ["NGINX_SHARED_SECRET"]	#the shared secret with nginx to generate the secure files

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

syslog = SysLogHandler(address='/dev/log',facility='mail')
formatter = logging.Formatter('%(asctime)s attext: %(levelname)-8s %(message)s', datefmt='%b %d %H:%M:%S')

syslog.setFormatter(formatter)
logger.addHandler(syslog)

#logging.basicConfig(format='%(asctime)-11s gar-nich saveFile(' + getpass.getuser() + '): %(levelname)-8s %(message)s', filename='/var/log/mail.log', datefmt='%b %d %H:%M:%S',level=logging.DEBUG)

### Shouldnt have to change a thing from here

email_body = ""
charset = ""
user = ""
downloadLink = ""
expires = ""
user = os.environ["SENDER"] #str(sys.argv[1:])
# source: https://stackoverflow.com/questions/12903893/python-imap-utf-8q-in-subject-string
def decode_mime_words(s): return u''.join(word.decode(encoding or 'utf8') if isinstance(word, bytes) else word for word, encoding in email.header.decode_header(s))
def sendmail(msgType,filename="",downloadLink="",expires=""):
    sender = os.environ["RECIPIENT"] #'downloads@gar-nich.net'
    recipient = os.environ["SENDER"]
    logging.debug("Sender: " + sender + " Empfänger: " + recipient)
    body = mail_Content(msgType, filename=filename,downloadLink=downloadLink,expires=expires)
    subject = body[body.find(':') + 2:body.find('\n')]
    body = body[body.find('\n'):]
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    # Split real name (which is optional) and email address parts
    #sender_name, sender_addr = parseaddr(sender)
    #recipient_name, recipient_addr = parseaddr(recipient)

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    #sender_name = str(email.header.Header(sender_name, header_charset))
    #recipient_name = str(email.header.Header(recipient_name, header_charset))

    # Make sure email addresses do not contain non-ASCII characters
    #sender = sender.encode('ascii')
    #recipient = recipient.encode('ascii')

    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = email.mime.text.MIMEText(body.encode('utf-8'), 'plain', 'utf-8') #body_charset)
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = email.header.Header(subject, 'utf-8') #header_charset)

    # Send the message via SMTP to localhost:25
    smtp = SMTP("localhost")
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()


'''
	headers = Parser().parsestr(mail_Content(msgType, filename=filename,downloadLink=downloadLink,expires=expires)) #.encode("ascii", "ignore").decode("ascii"))
	logging.debug(headers, file=sys.stderr)
	# Send the message via our own SMTP server.
	s = smtplib.SMTP('localhost')
#	s.send_message(msg.decode("utf-8"))
	s.send_message(headers)
	s.quit()
'''
def mail_Content(msg_type, filename="Do Not know! O_o",downloadLink="Arghh! I could guess one",expires=""):
    '''
    msg_type:
		help
		fail_date_invalid
		fail_date_not_found
		fail_no_files
		file_deleted
		file_delete_reminder
		not_authorized
		success
    '''
    if not expires:
    	expires = int(time.time())
    mailheader = 'From: <downloads@gar-nich.net>\nTo: <' + user + '>\n'
    mailtext = {
        "help": \
'''Subject: Die Downloadanleitung
Hallo Du da!

Du willst also eine Datei zum Download anbieten? Super, geht ganz einfach! Sagt zumindest Alex…
Die Datei, die Du hochlädst, wird eine begrenzte Gültigkeit haben und solange über diesen Link runterladbar sein. Danach wird Sie automatisch gelöscht.

So ist der Ablauf:
Du antwortest auf diese Mail, indem Du Dich an die Anleitung hältst, die Dateien anhängst und diese Mail (WICHTIG) von Deinem zugelassenen Account schickst(z.B.: @gar-nich.net,@stoelti.land). Du erhältst dann eine Mail zurück, indem sich der Download-Link befindet. 
Außerdem bekommst Du eine Nachricht, kurz bevor die Gültigkeit des Download-Links erlöscht und die Datei entfernt wird.(1 Woche).

Wie lange soll die Datei/en runterladbar bleiben?
Bitte anpassen! Falls nichts geändert wird, ist die Datei, siehe unten, 2 Monate lang runterladbar:
(Erlaubte Werte sind: Jahr Jahre Monat Monate Woche Wochen Tag Tage)

DAUER: 2 Monate
(Entweder hier ändern, oder selbst weiter oben eingeben(Auf Blockschrift und den Doppelpunkt achten). Der erste "DAUER:" Eintrag wird benutzt.)

Es gibt folgende Möglichkeiten:


Einzelne Datei hochladen:
-------------------------

- Oben bei Dauer angeben, bis wann die Datei runterladbar sein soll
- Datei an diese E-Mail anhängen
- Email an downloads@gar-nich.net/downloads@stoelti.land schicken


Mehrere Dateien hochladen und als Zip-Datei anbieten:
-----------------------------------------------------

- Oben im Betreff den Namen der zu erstellenden Zip-Datei eingeben.
- Oben bei Dauer angeben, bis wann die Datei runterladbar sein soll
- Dateien an diese E-Mail anhängen
- Email an downloads@gar-nich.net/downloads@stoelti.land schicken

Schönen Gruß,

 Der Download-Bot in froher Erwartung...
''',
        "fail_date_invalid": \
'''Subject: Dauer war ungültig
Moin Moin,

Sorry, dass ich mich schon so schnell wieder melde, aber irgendwie scheinst Du was falsch verstanden zu haben, was den Zeitraum angeht, wie lange die Datei verfügbar sein soll. Zumindest hab ich Dich nicht verstanden und konnte die angegebene Dauer nicht interpretieren. :’(

Zur Erinnerung: Erlaubt sind diverse Zahlen mit folgenden Zeitintervallen:

	- Tag
	- Tage
	- Woche
	- Wochen
	- Monat
	- Monate 


Beispiel: (Dauer: 4 Tage)

Also: Gleich nochmal probieren! 

Schönen Gruß,

   Der Der Download-Bot auf der Suche nach der Zeit…
''',
        "fail_date_not_found": \
'''Subject: Dauer wurde nicht gefunden
Moin Moin,

Sorry, dass ich mich schon so schnell wieder melde, aber irgendwie scheinst Du vergessen zu haben, den Zeitraum anzugeben, wie lange die Datei verfügbar sein soll. 
Zur Erinnerung: Erlaubt sind diverse Zahlen mit folgenden Zeitintervallen:

	- Tag
	- Tage
	- Woche
	- Wochen
	- Monat
	- Monate 
	- Jahr
	- Jahre

Beispiel: (Dauer: 4 Tage)

Also: Gleich nochmal probieren! 

Schönen Gruß,

   Der Der Download-Bot auf der Suche nach der Zeit…

''',
        "fail_no_files": \
'''Subject: Datei vergessen!
Moin Moin,

Sorry, dass ich mich schon so schnell wieder melde, aber anscheinend ist Dir grade das passiert, was mir auch ständig passiert:

Emails mit Anhängen verschicken wollen, und dann die Anhänge vergessen!

Auf jeden Fall kam hier nix an…

Schönen Gruß,

   Der Der Download-Bot auf der Suche nach Dateien…
''',
        "file_deleted": \
u' ' + '''Subject: Datei wurde gelöscht

Moin Moin,

die von Dir irgendwann mal hochgeladene Datei:

''' + filename + '''

ist abgelaufen und wurde soeben gelöscht!
Aber lade doch einfach eine neue hoch! 

Schönen Gruß, 

der Download-Bot, jetzt ein wenig ärmer...
''',
        "file_delete_reminder": 
'''Subject: ACHTUNG: Datei wird in ner Woche gelöscht
Moin Moin,

nur so zur Info, Deine von Dir am ''' + time.strftime('%A, den %d.%m.%y') + ''' hochgeladene Datei( ''' + filename + ''' ) wird in einer Woche gelöscht. Genauer am:

''' + time.strftime('%A, den %d.%m.%y',time.localtime(expires)) + '''

Also nochmal allen Bescheid sagen, dass Sie jetzt nochmal runterladen sollen. Der Link dafür ist:

''' + downloadLink + '''

Schönen Gruß,

Der Download-Bot, kurz vor'm Nirvana...

''',
        "not_authorized": \
'''Subject: Not Authorized
Moin Moin,

so geht’s ja nicht. Wahrscheinlich hast Du ja nur von einer nicht authorisierten Mail versendet, also einfach mit Deiner Standard-Mail nochmal probieren!
Da das ein nicht erlaubter Zugriffsversuch war, wird dieser Versuch auch an den Administrator gemeldet. 

Solltest Du wirklich versucht haben, diesen Dienst zu missbrauchen:

        __   
       /  \      
       |  |
       |  |
     __|  |__
    /  |  |  \__ 
  __|  |  |  |  |
 /  /        |  |
 |              |
 \              |
  \             /
   \___________/

     FUCK OFF!

     
Schönen Gruß,

   Der Der Download-Bot auf der Suche nach netten E-Mail-Adressen…
''',
        "success": \
'''Subject: Hier ist der Link zur Datei (''' + filename + ''')
Moin Moin,

und da haben wir es ja schon! Die Dateien wurden erfolgreich hochgeladen und sind unter folgendem Link erreichbar:

''' + downloadLink + '''

unter dieser Adresse ist die Datei/en verfügbar bis zum:

''' + time.strftime('%d.%m.%y',time.localtime(expires)) + '''

Schönen Gruß und viel Spaß damit,

   Der Download-Bot, glücklich und zufrieden...

''',
    }
    return mailtext.get(msg_type, "nothing")

# getting the mail content

#REading Mail from stdin
for line in sys.stdin:
	email_body += line
	line = line.lower()
	'''if "charset" in line and not charset:
	if ($line =~ "charset"
	and $charset eq "") {
	chomp($line);
	$charset = substr $line, 9;
	binmode($fh, ":encoding($charset)") or warn "invalid Charset found"; #STDIN
	print $log "Charset: $charset\n";
	}
	'''
	if "subject" in line:
		if "help" in line or "hilfe" in line or "anleitung" in line:
			sendmail("help")
			sys.exit(1)
	elif "dauer:" in line:
		amount = float(line[line.index("dauer:") + 7:].strip().split(maxsplit=1)[0])
		if "tag" in line:
			expires = str(int(time.mktime((datetime.datetime.now() + datetime.timedelta(days=amount)).timetuple())))
		elif "woche" in line:
			expires = str(int(time.mktime((datetime.datetime.now() + datetime.timedelta(weeks=amount)).timetuple())))
		else:
			sendmail("fail_date_invalid")
			sys.exit(1)
#		expires = int(time.time() + wordInSeconds * float(line[line.index("dauer:") + 7:].strip().split(maxsplit=1)[0]))
# checking collected data. Anything missing?
# help
# fail_date_invalid
# fail_date_not_found
# fail_no_files
# file_deleted
# file_delete_reminder
# not_authorized
# success

if not user:
	sendmail("not_authorized")
	sys.exit(1)
if not expires:
	sendmail("fail_date_not_found")
	sys.exit(1)

# parsing the mail content to get a mail object
mail = email.message_from_string(email_body)
# check if any attachments at all

#if mail.get_content_maintype() != 'multipart':
# we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
for part in mail.walk():
	# multipart are just containers, so we skip them
	if part.get_content_maintype() == 'multipart':
		continue
	# is this part an attachment?
	if part.get('Content-Disposition') is None:
		continue
	filename = part.get_filename()
	if "p7s" in filename.lower():
		continue
	counter = 1
	# if there is no filename, we create one with a counter to avoid duplicates
	if not filename:
		filename = 'part-%03d%s' % (counter, 'bin')
		counter += 1
	# getting mail date
	filename = decode_mime_words(u''+filename)
	#filename = urllib.parse.quote_plus(filename)
	att_path = os.path.join(outputdir, filename)
	mail_path = os.path.join(outputdir,".futuremails","")
	# check if output directory exists
	if not os.path.isdir(mail_path): os.makedirs(mail_path)

	# check if its already there
	i = 0
	while os.path.isfile(att_path):
		i += 1
		att_path = os.path.join(outputdir, filename + "_" + str(i))
	if i > 0:
		filename = filename + "_" + str(i)

	logging.debug('Saving to ' + str(att_path))
	# finally write the stuff
	oldmask = os.umask (11)
	with open(att_path, 'wb') as fp:
		fp.write(part.get_payload(decode=True))
	#create downloadlink
	os.umask (oldmask)
	byte_string = (str(expires)  + str("/" + filename) + str(" " + nginx_secret)).encode('utf-8')
	hashed_string = hashlib.md5( byte_string ).digest()
	link = base64.b64encode(hashed_string).decode("utf-8")
	link = link.replace('+', '-').replace('/', '_').replace("=", "")
	
	logging.debug("secret: " + str(link)) 
	logging.debug("nginx_url: " + str(nginx_url))
	logging.debug("filename: " + str(filename)) 
	logging.debug("expires: " + str(expires)) 

	downloadLink = nginx_url + str("/" + filename) + "?md5=" + str(link) + "&expires=" + str(expires);
	logging.debug("Download-Link: " + str(downloadLink)) 
	# 1 week Warningdate in Crontab: time.strftime('%M %H %d %m *',time.localtime(expires - 604800))
	if time.time() < (int(expires) - 605000):
		cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(int(expires) - 604800)) + " sendmail " + user + " < " + os.path.join(outputdir, ".futuremails", "") + str(expires) + filename + "-warning.mail') | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write cronjobs to send the mails: (crontab -l && echo "0 0 0 0 0 sendmail $user < $Downloadfolder/.futuremails/$timestamp.mail") | crontab - 
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(int(expires))) + " sendmail " + user + " < " + os.path.join(outputdir, ".futuremails", "") + str(expires)  + filename +  "-deleted.mail') | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write out cronjob to delete the file: 
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(int(expires) + 7100)) + " rm -f " + att_path + "              #Time in Epoch:" + str(expires) + " !!Dont remove!!')  | crontab -", shell=True, stderr=subprocess.STDOUT)
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(int(expires) + 7100)) + " rm -f " + os.path.join(mail_path, str(expires) + "*") + "')  | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write cronjob to remove entry from crontab : (crontab -l && echo "0 0 0 0 0 ( crontab -l | grep -v -F "$timestamp.mail" ) | crontab -") | crontab -
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(int(expires) + 7200)) + " ( crontab -l | grep -v -F " + str(expires) + " ) | crontab -') | crontab -", shell=True, stderr=subprocess.STDOUT)
	#write out future mails:
	if time.time() < (int(expires) - 605000):
		with open(os.path.join(mail_path, str(expires) + filename + "-warning.mail"),mode='w', encoding='utf-8') as out:
			out.write(mail_Content("file_delete_reminder",filename=filename,downloadLink=downloadLink,expires=int(expires)))
	with open(os.path.join(mail_path, str(expires) + filename + "-deleted.mail"),mode='w', encoding='utf-8') as out:
		out.write(mail_Content("file_deleted",filename=filename,downloadLink=downloadLink,expires=int(expires)))
	
	sendmail("success",filename=filename,downloadLink=downloadLink,expires=int(expires))

# help
# fail_date_invalid
# fail_date_not_found
# fail_no_files
# file_deleted
# file_delete_reminder
# not_authorized
# success

# schedule future mails:
# expire-date in Crontab: time.strftime('%M %H %d %m *',time.localtime(expires))
# write mail with timestamp as name to $Downloadfolder/.futuremails

'''
worked: everything deleted itself
1 2 3 4 5 some entry
1 * * * * ( crontab -l | grep -v -F some ) | crontab -

'''



