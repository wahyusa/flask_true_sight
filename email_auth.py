from __future__ import print_function

import os.path
import os
import base64

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']


def sendVerificationCode(verification_number, receiver):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEMultipart('alternative')
        message['To'] = receiver
        message['From'] = os.getenv('EMAIL')
        message['Subject'] = 'Automated draft'
        
        BODY = """
<html>
    <head>
        <style>
            .box{
                background-color: darkorange;
                height: auto;
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                padding: 10px 20px 10px 20px;
                color: white;
            }
            p {
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            }
            .grayed{
                color: gray;
            }
        </style>
    </head>
    <body>
        
        <div class="box"><h1>True Sight Verification Code</h1></div>
        <p>You're tyring to reset your password. Your verification code is: <b>""" + verification_number +"""</b>.</p>

        <p>Please complete the account verification process in 30 minutes.</p> 

        <p class="grayed"><u><b>This is an automated email. Please do not reply to this email.</b></u></p> 
    </body>
</html>
        """
        
        HTML_BODY = MIMEText(BODY, 'html')
        message.attach(HTML_BODY)

        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body={'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
        
def sendVerificationCode(verification_number, receiver):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEMultipart('alternative')
        message['To'] = receiver
        message['From'] = os.getenv('EMAIL')
        message['Subject'] = 'Automated draft'
        
        BODY = """
<html>
    <head>
        <style>
            .box{
                background-color: darkorange;
                height: auto;
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                padding: 10px 20px 10px 20px;
                color: white;
            }
            p {
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            }
            .grayed{
                color: gray;
            }
        </style>
    </head>
    <body>
        
        <div class="box"><h1>True Sight Verification Code</h1></div>
        <p>You're tyring to reset your password. Your verification code is: <b>""" + verification_number +"""</b>.</p>

        <p>Please complete the account verification process in 30 minutes.</p> 

        <p class="grayed"><u><b>This is an automated email. Please do not reply to this email.</b></u></p> 
    </body>
</html>
        """
        
        HTML_BODY = MIMEText(BODY, 'html')
        message.attach(HTML_BODY)

        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body={'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
        
def sendVerificationCode(verification_number, receiver):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEMultipart('alternative')
        message['To'] = receiver
        message['From'] = os.getenv('EMAIL')
        message['Subject'] = 'True Sight Verification Code'
        
        BODY = """
<html>
    <head>
        <style>
            .box{
                background-color: darkorange;
                height: auto;
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                padding: 10px 20px 10px 20px;
                color: white;
            }
            p {
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            }
            .grayed{
                color: gray;
            }
        </style>
    </head>
    <body>
        
        <div class="box"><h1>True Sight Verification Code</h1></div>
        <p>You're tyring to reset your password. Your verification code is: <b>""" + verification_number +"""</b>.</p>

        <p>Please complete the account verification process in 30 minutes.</p> 

        <p class="grayed"><u><b>This is an automated email. Please do not reply to this email.</b></u></p> 
    </body>
</html>
        """
        
        HTML_BODY = MIMEText(BODY, 'html')
        message.attach(HTML_BODY)

        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body={'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}).execute())
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
        
def sendVerificationEmail(link_verification, receiver):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        service = build('gmail', 'v1', credentials=creds)
        message = MIMEMultipart('alternative')
        message['To'] = receiver
        message['From'] = os.getenv('EMAIL')
        message['Subject'] = 'True Sight Email Verification'
        
        BODY = """
<html>
    <head>
        <style>
            .box{
                background-color: darkorange;
                height: auto;
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
                padding: 10px 20px 10px 20px;
                color: white;
            }
            p {
                font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            }
            .grayed{
                color: gray;
            }
            .box-center {
                display: block;
                position: absolute;
                left: 50%;
                transform: translate(-50%,0);
            }
            .container{
                padding: 20px;
            }
        </style>
    </head>
    <br>
        <div class="box-center">
            <div class="box"><center><h1>True Sight Email Verification</h1></center></div>
            <div class="container">
                <p>Keep your True sight Account secure by verifying your email address.</p>
                <center><a href=\"""" + link_verification + """\" style="display: block; background-color: darkorange; color: white; padding: 10px; border-radius: 5px; font-style: normal; font-weight: bold; font-size: 24px; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif; text-decoration: none; margin-top: 20px; margin-bottom: 20px; width: fit-content;">Verify Email</a></center>
                <p class="grayed"><u><b>This is an automated email. Please do not reply to this email.</b></u></p> 
            </div>
        </div>
    </body>
</html>
        """
        
        HTML_BODY = MIMEText(BODY, 'html')
        message.attach(HTML_BODY)

        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body={'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}).execute())
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None