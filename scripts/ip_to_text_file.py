import ipgetter
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import gmtime, strftime

filename = 'external_ip'
dir = './data'
file_path = dir + '/' + filename
current_ip = None
host = 'smtp.gmail.com'
port = 587
subject = 'New IP : ' + strftime('%Y-%m-%d %H:%M:%S', gmtime())
password_path = '.\init_info\password'

with open(password_path, 'r') as temp_file:
    user = temp_file.readline()
    password = temp_file.readline()

def create_if_not_exist():
    try: 
        os.makedirs(dir)
    except OSError:
        if not os.path.isdir(dir):
            raise

def send_email(new_ip):
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = user
    msg.attach(MIMEText(new_ip, 'text'))
    
    server = smtplib.SMTP(host, port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(user, password)
    server.sendmail(user, user, msg.as_string())
    server.quit()
    
    
create_if_not_exist()
if os.path.exists(file_path):  
    current_ip = open(file_path, "r").read() 
    os.remove(file_path)

new_ip = ipgetter.myip()

if new_ip != current_ip:
    print 'New IP detected {}'.format(new_ip)
    send_email(new_ip)
    out_file = open(file_path, 'w+')
    out_file.write(new_ip)
    out_file.close()
    print 'New IP saved and email sent.'
else:
    print 'No changes in IP'
    