"""
OAuth2 flow for Google Calendar authentication.
"""

from google_auth_oauthlib.flow import Flow
from django.conf import settings

from .constants import SCOPES
from .exceptions import OAuthError


def get_oauth_flow() -> Flow:
    """
    Create and return a Google OAuth2 flow for Calendar API.
    
    Requires the following Django settings:
        - GOOGLE_CLIENT_ID
        - GOOGLE_CLIENT_SECRET
        - GOOGLE_REDIRECT_URI
        
    Returns:
        google_auth_oauthlib.flow.Flow object configured for Calendar API
        
    Raises:
        OAuthError: If required settings are missing
    """
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', None)
    client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
    redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', None)
    
    if not all([client_id, client_secret, redirect_uri]):
        raise OAuthError(
            "Missing required settings: GOOGLE_CLIENT_ID, "
            "GOOGLE_CLIENT_SECRET, and GOOGLE_REDIRECT_URI must be configured"
        )
    
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    
    try:
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        return flow
    except Exception as e:
        raise OAuthError(f"Failed to create OAuth flow: {str(e)}")

