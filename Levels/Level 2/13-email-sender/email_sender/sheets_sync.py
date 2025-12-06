"""
Google Sheets synchronization module.

This module provides functionality to sync recipient data from Google Sheets.
"""

import logging
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from .auth_service import (
    is_google_api_available,
    require_google_api,
    GoogleAuthService,
    SHEETS_READONLY_SCOPES,
)

# Re-export for backwards compatibility
SHEETS_AVAILABLE = is_google_api_available()

logger = logging.getLogger(__name__)


class SheetsSync:
    """Google Sheets synchronization handler."""

    def __init__(
        self, credentials_path: Optional[str] = None, token_path: Optional[str] = None
    ):
        """
        Initialize Sheets sync.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token
        """
        require_google_api()

        self._auth_service = GoogleAuthService(
            credentials_path=credentials_path,
            token_path=token_path,
        )
        self.service = self._auth_service.get_service(
            service_name="sheets",
            version="v4",
            scopes=SHEETS_READONLY_SCOPES,
        )

    def extract_sheet_id(self, sheet_url: str) -> str:
        """
        Extract sheet ID from Google Sheets URL.

        Args:
            sheet_url: Full Google Sheets URL

        Returns:
            Sheet ID
        """
        # Handle different URL formats
        if "/d/" in sheet_url:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
        elif "spreadsheets/d/" in sheet_url:
            sheet_id = sheet_url.split("spreadsheets/d/")[1].split("/")[0]
        else:
            # Assume it's already a sheet ID
            sheet_id = sheet_url

        return sheet_id.strip()

    def read_sheet(
        self, sheet_id: str, range_name: str = "A1:Z1000"
    ) -> List[Dict[str, Any]]:
        """
        Read data from a Google Sheet.

        Args:
            sheet_id: Google Sheet ID
            range_name: Range to read (e.g., "Sheet1!A1:Z1000")

        Returns:
            List of dictionaries with column headers as keys
        """
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=sheet_id, range=range_name)
                .execute()
            )

            values = result.get("values", [])

            if not values:
                logger.warning(f"No data found in sheet {sheet_id}")
                return []

            # First row is headers
            headers = [h.strip().lower() for h in values[0]]
            if "email" not in headers:
                raise ValueError("Sheet must have an 'email' column")

            # Convert rows to dictionaries
            recipients = []
            for i, row in enumerate(values[1:], start=2):
                if not row or not any(row):
                    continue  # Skip empty rows

                # Pad row to match headers length
                row = row + [""] * (len(headers) - len(row))

                recipient = {}
                for header, value in zip(headers, row):
                    recipient[header] = value.strip() if value else ""

                # Validate email
                email = recipient.get("email", "").strip()
                if not email:
                    logger.warning(f"Row {i}: Missing email, skipping")
                    continue

                recipients.append(recipient)

            logger.info(f"Read {len(recipients)} recipients from sheet {sheet_id}")
            return recipients

        except HttpError as e:
            logger.error(f"Error reading sheet: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error reading sheet: {e}")
            raise

    def sync_to_campaign(
        self, storage, campaign_id: int, sheet_id: str, range_name: str = "A1:Z1000"
    ) -> int:
        """
        Sync sheet data to a campaign.

        Args:
            storage: CampaignStorage instance
            campaign_id: Campaign ID to sync to
            sheet_id: Google Sheet ID
            range_name: Range to read

        Returns:
            Number of recipients added/updated
        """
        recipients = self.read_sheet(sheet_id, range_name)
        if recipients:
            added = storage.add_recipients(campaign_id, recipients)
            storage.update_campaign_sync_time(campaign_id)
            return added
        return 0
