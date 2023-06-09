from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import webbrowser

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def add_to_calendar(task=None):
    
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
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        #now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        event_json = create_json(task)
        
        event = service.events().insert(calendarId='primary', body=event_json).execute()
        print(f"Event created: {event.get('htmlLink')}")
        webbrowser.open(event.get('htmlLink'))


    except HttpError as error:
        print('An error occurred: %s' % error)

def create_json(taskObj):

    date_str = taskObj.deadline.strftime('%Y-%m-%d %H:%M:%S')
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    end_obj = date_obj + datetime.timedelta(hours=1)

    start_date_str = date_obj.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=2))).isoformat()
    end_date_str = end_obj.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=2))).isoformat()

    event = {
        'summary': taskObj.title,
        'location': 'Wrocław, Polska',
        'description': taskObj.description,
        'start': {
            "dateTime": start_date_str,
            'timeZone': 'Europe/Berlin',
        },
        'end': {
            "dateTime": end_date_str,
            'timeZone': 'Europe/Berlin',
        },
        'recurrence': [
            'RRULE:FREQ=DAILY;COUNT=1'
        ],
        'attendees': [
            {'email': taskObj.author.email},
        ],
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 24 * 60},
            {'method': 'popup', 'minutes': 10},
            ],
        },
    }
    return event
