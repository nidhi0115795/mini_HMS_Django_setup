"""
Google Calendar event creation service.
"""

from datetime import datetime
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from .exceptions import CalendarEventError
from .utils import to_google_datetime


def create_calendar_event(
    credentials: Credentials,
    title: str,
    description: str,
    start_time: datetime,
    end_time: datetime,
    timezone: str = "UTC"
) -> dict:
    """
    Create a Google Calendar event.
    
    Args:
        credentials: Google OAuth2 Credentials object
        title: Event title/summary
        description: Event description
        start_time: Event start datetime
        end_time: Event end datetime
        timezone: Timezone for the event (default: UTC)
        
    Returns:
        Created event data from Google Calendar API
        
    Raises:
        CalendarEventError: If event creation fails
        
    Integration Point:
        Call this function after a booking is confirmed.
        Example usage in booking confirmation:
        
            from integrations.google_calendar import (
                create_calendar_event,
                build_credentials,
                CalendarEventError
            )
            
            # Assuming user has stored OAuth tokens
            token_data = {
                'access_token': user.google_access_token,
                'refresh_token': user.google_refresh_token,
            }
            credentials = build_credentials(token_data)
            
            try:
                event = create_calendar_event(
                    credentials=credentials,
                    title=f"Appointment with Dr. {doctor.name}",
                    description=f"Booking ID: {booking.id}",
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                )
            except CalendarEventError as e:
                logger.error(f"Failed to create calendar event: {e}")
    """
    if not credentials:
        raise CalendarEventError("Credentials are required")
    
    event_body = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': to_google_datetime(start_time),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': to_google_datetime(end_time),
            'timeZone': timezone,
        },
    }
    
    try:
        service = build('calendar', 'v3', credentials=credentials)
        event = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()
        return event
    except HttpError as e:
        raise CalendarEventError(f"Google Calendar API error: {e.reason}")
    except Exception as e:
        raise CalendarEventError(f"Failed to create calendar event: {str(e)}")

