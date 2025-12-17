"""
Utility functions for Google Calendar integration.
"""

from datetime import datetime, timezone


def to_google_datetime(dt: datetime) -> str:
    """
    Convert a datetime object to Google Calendar API format (RFC3339).
    
    If the datetime is naive (no timezone info), UTC is assumed.
    
    Args:
        dt: A datetime object (naive or timezone-aware)
        
    Returns:
        ISO 8601 formatted string with timezone info
    """
    if dt.tzinfo is None:
        # Naive datetime - assume UTC
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat()

