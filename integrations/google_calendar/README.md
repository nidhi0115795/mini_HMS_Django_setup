# Google Calendar Integration Module

This module provides Google Calendar integration for the Mini HMS Django project, enabling OAuth2 authentication and calendar event creation for appointment bookings.

## What This Module Does

- **OAuth2 Authentication**: Connects user Google accounts (Doctors/Patients) via OAuth2
- **Token Management**: Builds credentials from stored OAuth tokens
- **Event Creation**: Creates Google Calendar events when bookings are confirmed

## Module Structure

```
integrations/google_calendar/
├── __init__.py          # Public API exports
├── constants.py         # API scopes
├── exceptions.py        # Custom exceptions
├── utils.py             # Utility functions (datetime conversion)
├── token_store.py       # Credential building from stored tokens
├── oauth.py             # OAuth2 flow setup
├── calendar_service.py  # Calendar event creation
└── README.md            # This file
```

## Required Environment Variables

Add these to your Django settings:

```python
# settings.py
GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret"
GOOGLE_REDIRECT_URI = "http://localhost:8000/oauth/callback/"
```

**Important**: Never commit secrets to version control. Use environment variables:

```python
import os

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
```

## OAuth Flow

### 1. Initiate OAuth (in your views)

```python
from integrations.google_calendar import get_oauth_flow

def google_auth_view(request):
    flow = get_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)
```

### 2. Handle OAuth Callback (in your views)

```python
from integrations.google_calendar import get_oauth_flow

def google_callback_view(request):
    flow = get_oauth_flow()
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    
    # Store tokens in user model (implement based on your User model)
    user.google_access_token = credentials.token
    user.google_refresh_token = credentials.refresh_token
    user.save()
```

### 3. Create Calendar Event on Booking Confirmation

```python
from integrations.google_calendar import (
    create_calendar_event,
    build_credentials,
    CalendarEventError
)

def confirm_booking(booking):
    """
    INTEGRATION POINT: Call this after booking is confirmed.
    Add this to your booking confirmation logic.
    """
    user = booking.patient  # or booking.doctor
    
    # Build credentials from stored tokens
    token_data = {
        'access_token': user.google_access_token,
        'refresh_token': user.google_refresh_token,
    }
    credentials = build_credentials(token_data)
    
    try:
        event = create_calendar_event(
            credentials=credentials,
            title=f"Appointment: {booking.doctor.name}",
            description=f"Booking #{booking.id}\n{booking.notes}",
            start_time=booking.start_time,
            end_time=booking.end_time,
        )
        booking.google_event_id = event.get('id')
        booking.save()
    except CalendarEventError as e:
        # Log error but don't fail the booking
        logger.error(f"Calendar sync failed: {e}")
```

## Required Dependencies

Add to `requirements.txt`:

```
google-auth>=2.0.0
google-auth-oauthlib>=1.0.0
google-api-python-client>=2.0.0
```

## Error Handling

The module provides three exception types:

- `GoogleCalendarError`: Base exception for all calendar errors
- `OAuthError`: OAuth authentication/configuration errors
- `CalendarEventError`: Event creation failures

```python
from integrations.google_calendar import (
    CalendarEventError,
    OAuthError,
    GoogleCalendarError
)

try:
    event = create_calendar_event(...)
except OAuthError:
    # Handle OAuth issues (missing credentials, expired tokens)
    pass
except CalendarEventError:
    # Handle event creation issues
    pass
except GoogleCalendarError:
    # Catch-all for any calendar-related error
    pass
```

## Token Storage Assumptions

This module assumes tokens are stored in the User model or a related table with fields like:
- `google_access_token`
- `google_refresh_token`

The actual storage implementation should be handled by the accounts team.

