import imaplib
import email

with open('.\init_info\password', 'r') as temp_file:
    user = temp_file.readline().replace('\n', '')
    password = temp_file.readline().replace('\n', '')
    
with open('.\init_info\keywords', 'r') as temp_file:
    content = temp_file.readlines()
# remove \n
keywords = [x.strip() for x in content] 

server = imaplib.IMAP4_SSL('imap.gmail.com')
server.login(user, password)
server.select('inbox')

type, data = server.search(None, 'ALL')

if data == []:
    print 'Empty email inbox'
else:
    id_list = data[0].split() 
    first_email_id = int(id_list[0])
    last_email_id = int(id_list[-1])
    
    latest_date_time = None
    latest_ip = None
    
    uid_list = []
    
    for i in range(first_email_id, last_email_id+1):
        typ, data = server.fetch(i, '(RFC822)')
        email_msg = email.message_from_string(data[0][1])
        
        sent_to = email_msg['to']
        email_from = email_msg['from']
        subject = email_msg['subject']
        to_break = False    
        
        if user in email_from and subject is not None:
            for sub in keywords:
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
