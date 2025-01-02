import json
import requests
from datetime import datetime, timedelta, timezone
from incidentbot.configuration.settings import settings
from incidentbot.logging import logger


class GoogleMeeting:
    """Creates a Google Meet meeting"""

    def __init__(self, incident: str, client_id: str, client_secret: str, redirect_uri: str):
        self.incident = incident
        self.endpoint = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        self._token = None  # Cache the token
        self.headers = {
            "authorization": None,
            "content-type": "application/json",
        }
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def __get_token(self) -> str:
        """Generate and cache the OAuth2 token."""
        if not self._token:
            self._token = self.__generate_token()
            if self._token:
                logger.debug(f"Token successfully generated: {self._token}")
                self.headers["authorization"] = f"Bearer {self._token}"
            else:
                logger.error("Failed to generate a valid token.")
        return self._token

    def __create(self) -> str:
        """Create a Google Meet meeting and return its URL."""
        logger.debug("Starting the Google Meet meeting creation process.")

        if not self.__get_token():
            logger.error("No valid token available for creating the meeting.")
            return None

        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(hours=1)

        meeting_details = {
            "summary": self.incident,
            "description": f"Incident meeting for: {self.incident}",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "UTC"},
            "conferenceData": {
                "createRequest": {
                    "requestId": f"incident-{start_time.timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
        }

        try:
            logger.debug(f"Sending request to {self.endpoint} with meeting details: {meeting_details}")
            res = requests.post(
                self.endpoint,
                headers=self.headers,
                params={"conferenceDataVersion": 1},
                data=json.dumps(meeting_details),
            )

            res_json = res.json()
            logger.debug(f"Response received: {res_json}")

            if res.status_code != 200:
                logger.error(f"Error creating Google Meet meeting: {res.status_code}, {res_json}")
                return None

            if "conferenceData" not in res_json or "entryPoints" not in res_json["conferenceData"]:
                logger.error("Error creating Google Meet meeting: Missing 'conferenceData' or 'entryPoints' in response.")
                return None

            return res_json["conferenceData"]["entryPoints"][0]["uri"]
        except Exception as error:
            logger.error(f"Error creating Google Meet meeting: {error}")
            return None


    def __generate_token(self) -> str:
        """Generate an OAuth2 token using a service account or user credentials."""
        try:
            endpoint = "https://oauth2.googleapis.com/token"
            payload = {
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": settings.GOOGLE_REFRESH_TOKEN,
            }
            res = requests.post(endpoint, data=payload)

            if res.status_code == 200 and "access_token" in res.json():
                return res.json()["access_token"]
            else:
                logger.error(f"Error fetching Google OAuth token: {res.status_code}, {res.json()}")
                return None
        except Exception as error:
            logger.error(f"Error generating token for Google API: {error}")
            return None

    @property
    def url(self) -> str:
        """Create and return the Google Meet URL."""
        url = self.__create()
        return url

    def test_auth(self) -> bool:
        """Test if authentication works by ensuring a valid token can be generated."""
        token = self.__get_token()
        return token is not None
