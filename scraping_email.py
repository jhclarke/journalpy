#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from socket import gaierror
from datetime import date
import json
import touch
import os
import shutil

# Part 2 of scraping process below (only once per week)

#--------------
# USER Input
#--------------
username = '' # System username
user_servername = 'GMail' # Gmail or whatever server you use
user_send = '' # Email address to send from
user_password = '' # Password to send email address
user_reciever = '' # Email to send to
user_recievername = '' # First name of recipient
#-------------
#-------------
'''
Time to email the results!
'''
#-------------
# Read in the weeks paper values
writepath = r'/home/%s/Documents/python/scraping/data.json' % username
with open(writepath, 'r') as json_file:
    fresults=json.load(json_file) # Dictionary with keys=journal and values=list(articles)

values={'servername':user_servername,'sender':user_send,'password':user_password,'reciever':user_reciever,'recievername':user_recievername}
### Credentials for sending email with sender account ###
if values['servername'] == "GMail":
    port = 465
    smtp_server = 'smtp.gmail.com'
login = values['sender']
password = values['password']

# Specify the sender’s and receiver’s email addresses:
sender = values['sender']
receiver = values['reciever']
subject = 'Papers Update'
# fnameout = zipname
receivername = values['recievername']

### Sending emails ###
message = MIMEMultipart()
message["From"] = sender
message["To"] = receiver
message["Subject"] = subject


# HTML Text format
papertext = ''
if len(fresults) != 0:
    for journal,papers in fresults.items():
        i=0
        while i < len(papers):
            paper = papers[i]
            if i==0:
                value = '''\
                        <b>%s</b>
                        <br><br>
                        - <a href=%s>%s</a>
                        <br><br>
                        ''' % (journal,paper['link'],paper['title'])
            else:
                value = '''\
                        - <a href=%s>%s</a>
                        <br><br>
                        ''' % (paper['link'],paper['title'])
            papertext+=value
            i+=1
else:
    papertext ='No new results. Check back next week!'
body = """\
    <html>
        <head></head>
        <body>
            <p> Hi %s, <br><br>
                Please find the journal findings for this period below.
                ---
                <br><br>
                """ % (receivername) + papertext + """
                --<br>
                Your friendly neighborhood Python
                <br><br><br>
                **This is an automated email, in case of any discrepancies please respond with details**
            </p>
        </body>
    </html>

"""
message.attach(MIMEText(body, "html"))
text = message.as_string()


try:
    # Send your message with credentials specified above
    with smtplib.SMTP_SSL(smtp_server, port) as server:
        server.login(login, password)
        server.ehlo()
        server.sendmail(sender, receiver, text)
except (gaierror, ConnectionRefusedError):
  # tell the script to report if your message was sent or which errors need to be fixed
    print('Failed to connect to the server. Bad connection settings?')
except smtplib.SMTPServerDisconnected:
    print('Failed to connect to the server. Wrong user/password?')
except smtplib.SMTPException as e:
    print('SMTP error occurred: ' + str(e))
else:
    print('Success')

# Create reference file to avoid week-to-week redundancy
#---------------------------------------------------------
if len(fresults) != 0:
    writeoldpath=writepath.replace('data','data_old')
    shutil.copy(writepath,writeoldpath)
else:
    pass
