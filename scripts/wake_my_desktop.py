import imaplib
import email

from datetime import datetime
from wakeonlan import wol

with open('.\init_info\settings', 'r') as temp_file:
    user = temp_file.readline().replace('\n', '')
    password = temp_file.readline().replace('\n', '')
    mac = temp_file.readline().replace('\n', '')
    port = int(temp_file.readline().replace('\n', ''))

server = imaplib.IMAP4_SSL('imap.gmail.com')
server.login(user, password)
server.select('inbox')

def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()

type, data = server.search(None, 'ALL')
id_list = data[0].split() 
first_email_id = int(id_list[0])
last_email_id = int(id_list[-1])

latest_date_time = None
latest_ip = None

for i in range(first_email_id, last_email_id+1):
    typ, data = server.fetch(i, '(RFC822)')
    email_msg = email.message_from_string(data[0][1])
    
    sent_to = email_msg['to']
    email_from = email_msg['from']
    subject = email_msg['subject']
    body = get_first_text_block(email_msg)
    
    try:
        if subject is not None:
            curr_date_time = datetime.strptime(subject, 'New IP : %Y-%m-%d %H:%M:%S')
            if latest_date_time is None or curr_date_time >= latest_date_time:
                latest_date_time = curr_date_time
                latest_ip = body
                print 'New IP : {}'.format(latest_ip) 
            
    except ValueError:
        if subject is None:
            print 'Email with no subject title found'
        else:
            print 'Email incorrect title found : {}'.format(subject)

print 'Most recent IP : {}'.format(latest_ip)

if latest_date_time is None:
    raise Exception('No IP found in email')

wol.send_magic_packet(mac, ip_address=latest_ip, port = port)