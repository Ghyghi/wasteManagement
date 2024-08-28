from datetime import *
import os
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
from dotenv import load_dotenv
from googleapiclient.errors import HttpError


# Load environment variables from .env file
load_dotenv()

# Define Google API scopes
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar']
ALL_SCOPES = GMAIL_SCOPES + CALENDAR_SCOPES

def get_credentials():
    creds = None
    env_folder = os.getenv('ENV_FOLDER')
    creds_path = os.path.join(env_folder, 'token.json')
    credentials_path = os.path.join(env_folder, 'credentials.json')

    if os.path.exists(creds_path):
        creds = Credentials.from_authorized_user_file(creds_path, ALL_SCOPES)
        print("Found token.json, loading credentials...")
    else:
        print("token.json not found, initiating OAuth flow...")

    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                print("Credentials expired, refreshing...")
            else:
                raise RefreshError("Token expired or revoked.")
        except RefreshError:
            print("RefreshError occurred. Reauthorizing...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, ALL_SCOPES)
            creds = flow.run_local_server(port=51912)
            print("OAuth flow completed, credentials obtained.")
            with open(creds_path, 'w') as token:
                token.write(creds.to_json())
                print("Credentials saved to token.json.")

    print('Credentials obtained with no issue')
    return creds

def get_gmail_service():
    print('Initial build of the gmail service')
    creds = get_credentials()
    print('Got credentials, start building the service')
    service = build('gmail', 'v1', credentials=creds)
    print("Gmail service built successfully.")
    return service

def get_calendar_service():
    creds = get_credentials()
    service = build('calendar', 'v3', credentials=creds)
    print("Calendar service built successfully.")
    return service

def send_email(user_email, subject, html_content):
    service = get_gmail_service()
    
    message = MIMEMultipart()
    message['to'] = user_email
    message['subject'] = subject
    message.attach(MIMEText(html_content, 'html'))
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}
    
    try:
        message = service.users().messages().send(userId='me', body=message_body).execute()
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print(f'An error occurred: {error}')
        return None
    
def create_calendar_reminder(user_emails, user_location, startdate, user_choice):
    service = get_calendar_service()
    
    try:
        if user_choice == 'weekly':
            recurrence_rule = 'RRULE:FREQ=WEEKLY;INTERVAL=1'
        elif user_choice == 'monthly':
            recurrence_rule = 'RRULE:FREQ=MONTHLY;INTERVAL=1'
        else:
            raise ValueError("Invalid recurrence frequency chosen")
        event = {
        'summary': 'Trash Pickup Reminder',
        'location': user_location,
        'description': 'Reminder: Your trash will be picked up today. Please ensure your trash bins are ready.',
        'start': {
            'dateTime': startdate,  # Whole day event start
            'timeZone': 'Africa/Harare',  # Time zone set to Harare
        },
        'end': {
            'dateTime': startdate,  # Whole day event end
            'timeZone': 'Africa/Harare',
        },
        'recurrence': [
            recurrence_rule  # Frequency based on user selection
        ],
        'attendees': [{'email': email} for email in user_emails],
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # Reminder 1 day before
                {'method': 'popup', 'minutes': 60},       # Reminder 1 hour before
            ],
        },
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return event

    except HttpError as error:
        print(f'An error occurred: {error}')

def send_email_notification(user_emails, summary):
    subject = f"New Reminder Created: {summary}"
    body = (
    f"Your reminder for your upcoming trash pickup at {user_location} has been created.\n"
    f"Summary: {summary}\n"
)
    for email in user_emails:
        send_email(email, subject, body)

# if __name__=="__main__":
#     get_credentials()
#     get_gmail_service()
#     get_calendar_service()
#     email='nagasaroghislaine3@gmail.com'
#     subject='Test Email'
#     html_content='This is a test'
#     send_email(email, subject, html_content)
#     user_emails =['nagasaroghislaine3@gmail.com', 'n.iyankijij@alustudent.com']
#     summary = 'remainder'
#     user_location = 'Kk191st, Kabeza'
#     startdate = '2024-08-22T00:00:00+02:00'
#     user_choice = 'weekly'
#     create_calendar_reminder(user_emails, user_location, startdate, user_choice)
#     send_email_notification(user_emails, summary)