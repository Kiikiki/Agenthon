from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

scopes = ['https://www.googleapis.com/auth/gmail.readonly']

# let it call Gmail API to read email
def authenticateGmail(credentialFile, port):
    flow = InstalledAppFlow.from_client_secrets_file(credentialFile, scopes)
    credentials = flow.run_local_server(port=port)
    service = build('gmail', 'v1', credentials=credentials)

    return service

# get emails
def getEmails(service):
    # read emails
    emailList = service.users().messages().list(userId='me').execute()
    messages = emailList.get('messages', [])
    
    # get email content
    emails = []
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id']).execute()
        emails.append(txt)

    return emails

# filter
def thisWeekEmail(emails):
    week = time.time() - 7*24*3600
    
    return [
        email for email in emails
        if int(email['internalDate']) / 1000 > week
    ]



