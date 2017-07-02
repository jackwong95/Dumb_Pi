import ipgetter
import os
import smtplib
import credentials
import socket
import email
import signal
import imaplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime

file_path = './data/external_ip'
current_ip = None
host = 'smtp.gmail.com'
port = 587
subject = 'New IP : ' + strftime('%Y-%m-%d %H:%M:%S', gmtime())
time_limit = 60
REMOTE_SERVER = "www.google.com"

def has_internet():
  try:
    # see if we can resolve the host name -- tells us if there is
    # a DNS listening
    host = socket.gethostbyname(REMOTE_SERVER)
    # connect to the host -- tells us if the host is actually
    # reachable
    s = socket.create_connection((host, 80), 2)
    return True
  except:
     pass
  return False

class timeout_exception(Exception):
    pass

def timeout_handler(signum, frame):
    raise timeout_exception

def send_email():
    current_ip = None
    if os.path.exists(file_path):  
        current_ip = open(file_path, "r").read() 
    
    new_ip = ipgetter.myip()
    
    if current_ip is None or new_ip != current_ip:
        print 'New IP detected {}'.format(new_ip)
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = credentials.email_login['user']
        msg['To'] = credentials.email_login['user']
        msg.attach(MIMEText(new_ip, 'text'))
        
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(credentials.email_login['user'], credentials.email_login['pass'])
        server.sendmail(credentials.email_login['user'], credentials.email_login['user'], msg.as_string())
        server.quit()
        print 'New IP sent'
        
        if os.path.exists(file_path): 
            out_file = open(file_path, 'w+')
            out_file.write(new_ip)
            out_file.close()
        
            print 'New IP saved'
    else:
        print 'No changes in IP'

def delete_emails():
    server = imaplib.IMAP4_SSL('imap.gmail.com')
    server.login(credentials.email_login['user'], credentials.email_login['pass'])
    server.select('inbox')
    
    type, data = server.search(None, 'ALL')
    
    if data == ['']:
        print 'Empty email inbox'
    else:
        id_list = data[0].split() 
        first_email_id = int(id_list[0])
        last_email_id = int(id_list[-1])
        
        uid_list = []
        
        for i in range(first_email_id, last_email_id+1):
            typ, data = server.fetch(i, '(RFC822)')
            
            email_msg = email.message_from_string(data[0][1])
            email_from = email_msg['from']
            subject = email_msg['subject']
            
            to_break = False
            
            if email_from is not None and email_from == credentials.email_login['user'] and subject is not None:
                for sub in credentials.keywords:
                    if sub in subject:
                        to_break = True
                        break
                    
            if to_break:
                continue
            
            print 'Deleting {}'.format(subject)
            uid_list.append(i)
        
        if len(uid_list) == 0:
            print 'No spam email found'
        else:
            server.store(''.join(str(e)+',' for e in uid_list)[:-1], '+X-GM-LABELS', '\\Trash')
            server.expunge() 
            server.close()
            server.logout()

if has_internet():
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(time_limit)
        send_email()
        delete_emails()
        signal.alarm(0) #reset alarm
    except timeout_exception:
        print 'Time limit exceeded'
        exit()
else:
    print 'No internet connection'