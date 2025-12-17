from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
from datetime import datetime
import json
import os


CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/calendar']


def _build_flow(redirect_uri):
    if os.path.exists(CLIENT_SECRETS_FILE):
        return Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=SCOPES,
    )


def get_google_auth_url(redirect_uri):
    flow = _build_flow(redirect_uri)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return authorization_url, state


def exchange_code_for_tokens(code, redirect_uri):
    flow = _build_flow(redirect_uri)
    flow.fetch_token(code=code)
    credentials = flow.credentials
    return credentials.token, credentials.refresh_token


def get_calendar_service(access_token, refresh_token):
    token_uri = "https://oauth2.googleapis.com/token"
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    if os.path.exists(CLIENT_SECRETS_FILE):
        try:
            with open(CLIENT_SECRETS_FILE, 'r') as f:
                client_config = json.load(f)
            token_uri = client_config['web'].get('token_uri', token_uri)
            client_id = client_config['web'].get('client_id', client_id)
            client_secret = client_config['web'].get('client_secret', client_secret)
        except Exception:
            pass

    credentials = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    return build('calendar', 'v3', credentials=credentials)


def create_calendar_event(access_token, refresh_token, event_details):
    try:
        service = get_calendar_service(access_token, refresh_token)
        event = {
            'summary': event_details['summary'],
            'description': event_details.get('description', ''),
            'start': {
                'dateTime': event_details['start_datetime'].isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': event_details['end_datetime'].isoformat(),
                'timeZone': 'UTC',
            },
        }
        if 'attendee_email' in event_details:
            event['attendees'] = [{'email': event_details['attendee_email']}]
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        return created_event.get('id')
    except Exception as e:
        print(f"Error creating calendar event: {e}")
        return None


def delete_calendar_event(access_token, refresh_token, event_id):
    try:
        service = get_calendar_service(access_token, refresh_token)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting calendar event: {e}")
        return False
