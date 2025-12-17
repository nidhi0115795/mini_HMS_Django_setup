"""
Token storage utilities for Google OAuth credentials.
"""

from google.oauth2.credentials import Credentials
from django.conf import settings

from .exceptions import OAuthError

TOKEN_URI = "https://oauth2.googleapis.com/token"


def build_credentials(token_data: dict) -> Credentials:
    """
    Build Google OAuth2 Credentials from stored token data.
    
    Args:
        token_data: Dictionary containing OAuth token information:
            - access_token (required): The access token
            - refresh_token (optional): The refresh token
            - token_uri (optional): Token endpoint URI
            - expiry (optional): Token expiry datetime
            
    Returns:
        google.oauth2.credentials.Credentials object
        
    Raises:
        OAuthError: If required token data is missing
    """
    if not token_data or 'access_token' not in token_data:
        raise OAuthError("Missing access_token in token data")
    
    try:
        credentials = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri=token_data.get('token_uri', TOKEN_URI),
            client_id=getattr(settings, 'GOOGLE_CLIENT_ID', None),
            client_secret=getattr(settings, 'GOOGLE_CLIENT_SECRET', None),
        )
        return credentials
    except Exception as e:
        raise OAuthError(f"Failed to build credentials: {str(e)}")

