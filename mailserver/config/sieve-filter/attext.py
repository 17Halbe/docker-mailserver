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
from email import header

### Adjust to your needs:
#t[t.find("."):]
try: 
	host=os.environ["HOST"]
except:
	host="mx.localhost"

outputdir="/var/attachments"  						# local Location to save the attachments to. Has to be writable by user: docker 
nginx_url = "https://downloads" + host[host.find("."):]
#nginx_url = "https://downloads." +  os.environ["NGINX_DOWNLOAD_DOMAIN"]			#the download url 
nginx_secret = "<YOUR NGINX-SECRET>" #os.environ["NGINX_SHARED_SECRET"]	#the shared secret with nginx to generate the secure files


### Shouldnt have to change a thing from here

email_body = ""
charset = ""
user = ""
downloadLink = ""
expires = ""
user =str(sys.argv[1:])

# source: https://stackoverflow.com/questions/12903893/python-imap-utf-8q-in-subject-string
def decode_mime_words(s): return u''.join(word.decode(encoding or 'utf8') if isinstance(word, bytes) else word for word, encoding in email.header.decode_header(s))
def sendmail(msgType,filename="",downloadLink="",expires=""):
	
	# Open a plain text file for reading.  For this example, assume that
	# the text file contains only ASCII characters.
	headers = Parser().parsestr(mail_Content(msgType, filename=filename,downloadLink=downloadLink,expires=expires))

	# Send the message via our own SMTP server.
	s = smtplib.SMTP('localhost')
	s.send_message(msg)
	s.quit()

	#print (headers)
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
'''Subject: Hier ist der Link zur Datei ''' + filename + '''

Moin Moin,

und da haben wir’s ja schon! Die Dateien wurden erfolgreich hochgeladen und sind unter folgendem Link erreichbar:

''' + downloadLink + '''

unter dieser Adresse ist die Datei/en verfügbar bis:

''' + time.strftime('%A, den %d.%m.%y',time.localtime(expires)) + '''

Schönen Gruß und viel Spaß damit,

   Der Download-Bot, glücklich und zufrieden...

''',
    }
    return mailheader + mailtext.get(msg_type, "nothing")

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
		wordInSeconds = ""
		if "tag" in line:
			wordInSeconds = 86400
		elif "woche" in line:
			wordInSeconds = 604800
		elif "monat" in line:
			wordInSeconds = 2419200
		elif "jahr" in line:
			wordInSeconds = 31536000
		else:
			sendmail("fail_date_invalid")
			sys.exit(1)
		expires = int(time.time() + wordInSeconds * float(line[line.index("dauer:") + 7:].strip().split(maxsplit=1)[0]))
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
	counter = 1
	# if there is no filename, we create one with a counter to avoid duplicates
	if not filename:
		filename = 'part-%03d%s' % (counter, 'bin')
		counter += 1
	# getting mail date
	filename = decode_mime_words(u''+filename)
	att_path = os.path.join(outputdir, filename)
	mail_path = os.path.join(outputdir,".futuremails","")
	# check if output directory exists
	if not os.path.isdir(mail_path): os.makedirs(mail_path)

	# check if its already there
	i = 0
	while os.path.isfile(att_path):
		i += 1
		att_path = os.path.join(outputdir, filename + "_" + str(i))
	print ('Saving to', str(att_path))
	# finally write the stuff
	with open(att_path, 'wb') as fp:
		fp.write(part.get_payload(decode=True))

	#create downloadlink
	link = subprocess.check_output("/bin/echo -n '" + str(expires) + str(nginx_url) + str(nginx_secret) + "' | /usr/bin/openssl md5 -binary | /usr/bin/openssl base64 | /usr/bin/tr +/ -_ | /usr/bin/tr -d =", shell=True, stderr=subprocess.STDOUT)
	downloadLink = nginx_url + filename + "?md5=" + link.strip().decode("utf-8") + "&expires=" + str(expires);


	# 1 week Warningdate in Crontab: time.strftime('%M %H %d %m *',time.localtime(expires - 604800))
	if time.time() < (expires - 605000):
		cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(expires - 604800)) + " sendmail " + user + " < " + os.path.join(outputdir, ".futuremails", "") + str(expires) + filename + "-warning.mail') | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write cronjobs to send the mails: (crontab -l && echo "0 0 0 0 0 sendmail $user < $Downloadfolder/.futuremails/$timestamp.mail") | crontab - 
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(expires)) + " sendmail " + user + " < " + os.path.join(outputdir, ".futuremails", "") + str(expires)  + filename +  "-deleted.mail') | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write out cronjob to delete the file: 
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(expires + 7100)) + " rm -f " + att_path + "              #Time in Epoch:" + str(expires) + " !!Dont remove!!')  | crontab -", shell=True, stderr=subprocess.STDOUT)
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(expires + 7100)) + " rm -f " + os.path.join(mail_path, str(expires) + "*") + "')  | crontab -", shell=True, stderr=subprocess.STDOUT)
	# write cronjob to remove entry from crontab : (crontab -l && echo "0 0 0 0 0 ( crontab -l | grep -v -F "$timestamp.mail" ) | crontab -") | crontab -
	cron_result=subprocess.check_output("(crontab -l && echo '" + time.strftime('%M %H %d %m *',time.localtime(expires + 7200)) + " ( crontab -l | grep -v -F " + str(expires) + " ) | crontab -') | crontab -", shell=True, stderr=subprocess.STDOUT)
	#write out future mails:
	if time.time() < (expires - 605000):
		with open(os.path.join(mail_path, str(expires) + filename + "-warning.mail"),mode='w', encoding='utf-8') as out:
			out.write(mail_Content("file_delete_reminder",filename=filename,downloadLink=downloadLink,expires=expires))
	with open(os.path.join(mail_path, str(expires) + filename + "-deleted.mail"),mode='w', encoding='utf-8') as out:
		out.write(mail_Content("file_deleted",filename=filename,downloadLink=downloadLink,expires=expires))
	
	sendmail("success",filename=filename,downloadLink=downloadLink,expires=expires)

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



