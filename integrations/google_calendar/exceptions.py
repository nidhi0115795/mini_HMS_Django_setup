"""
Custom exceptions for Google Calendar integration.
"""


class GoogleCalendarError(Exception):
    """Base exception for Google Calendar integration errors."""
    pass


class OAuthError(GoogleCalendarError):
    """Exception raised for OAuth-related errors."""
    pass


class CalendarEventError(GoogleCalendarError):
    """Exception raised when calendar event creation fails."""
    pass

