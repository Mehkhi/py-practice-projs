"""
Google OAuth2 Authentication Service.

This module provides shared authentication functionality for Google APIs
(Gmail, Sheets, etc.) to eliminate code duplication.
"""

import logging
from pathlib import Path
from typing import Optional, List, Any

logger = logging.getLogger(__name__)

# Check if Google API libraries are available
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    Credentials = None
    InstalledAppFlow = None
    Request = None
    build = None
    HttpError = None


def is_google_api_available() -> bool:
    """Check if Google API libraries are installed."""
    return GOOGLE_API_AVAILABLE


def require_google_api():
    """Raise ImportError if Google API libraries are not available."""
    if not GOOGLE_API_AVAILABLE:
        raise ImportError(
            "Google API libraries not installed. "
            "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
        )


class GoogleAuthService:
    """
    Shared Google OAuth2 authentication service.

    Handles token loading, refresh, and OAuth2 flow for any Google API.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
    ):
        """
        Initialize authentication service.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
        """
        require_google_api()
        self.credentials_path = Path(credentials_path or "credentials.json")
        self.token_path = Path(token_path or "token.json")
        self._credentials = None

    def authenticate(self, scopes: List[str]) -> Credentials:
        """
        Authenticate with Google APIs using the specified scopes.

        Args:
            scopes: List of OAuth2 scopes to request

        Returns:
            Valid Google OAuth2 credentials
        """
        creds = None

        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(self.token_path), scopes
                )
                logger.debug(f"Loaded existing token from {self.token_path}")
            except Exception as e:
                logger.warning(f"Error loading token: {e}")

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token")
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download OAuth2 credentials from Google Cloud Console "
                        "and save as 'credentials.json'"
                    )
                logger.info("Running OAuth2 flow for new token")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), scopes
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use
            with open(self.token_path, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Saved new token to {self.token_path}")

        self._credentials = creds
        return creds

    def get_service(
        self,
        service_name: str,
        version: str,
        scopes: List[str],
    ) -> Any:
        """
        Get an authenticated Google API service.

        Args:
            service_name: Name of the Google service (e.g., 'gmail', 'sheets')
            version: API version (e.g., 'v1', 'v4')
            scopes: List of OAuth2 scopes to request

        Returns:
            Authenticated Google API service resource
        """
        creds = self.authenticate(scopes)
        service = build(service_name, version, credentials=creds)
        logger.info(f"Authenticated with {service_name} API ({version})")
        return service

    @property
    def credentials(self) -> Optional[Credentials]:
        """Get the current credentials (if authenticated)."""
        return self._credentials


# Pre-defined scope constants for convenience
GMAIL_SEND_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
GMAIL_READONLY_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SHEETS_READONLY_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SHEETS_READWRITE_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
