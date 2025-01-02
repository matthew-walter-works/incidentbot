import unittest
from incidentbot.google.meeting import GoogleMeeting


class TestGoogleMeetingIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup client credentials and meeting details."""
        cls.client_id = "your-client-id"  # Replace with your actual client ID
        cls.client_secret = "your-client-secret"  # Replace with your actual client secret
        cls.redirect_uri = "http://localhost"  # Replace with your actual redirect URI
        cls.incident = "Test Incident"

        # Initialize the GoogleMeeting instance
        cls.meeting = GoogleMeeting(
            cls.incident,
            cls.client_id,
            cls.client_secret,
            cls.redirect_uri,
        )

    def test_meeting_creation(self):
        """Test the creation of a Google Meet meeting."""
        # Attempt to create a meeting
        meet_url = self.meeting.url
        self.assertIsNotNone(meet_url, "Failed to create a Google Meet meeting.")
        self.assertTrue(
            meet_url.startswith("https://meet.google.com/"), "Invalid Google Meet URL."
        )
        print("Google Meet URL:", meet_url)

    def test_auth_token_generation(self):
        """Test if authentication token can be generated."""
        token = self.meeting.test_auth()
        self.assertTrue(token, "Failed to generate or validate authentication token.")
        print("Authentication token successfully generated and validated.")

    def test_invalid_token(self):
        """Test behavior with invalid credentials."""
        # Create a meeting instance with invalid credentials
        invalid_meeting = GoogleMeeting(
            self.incident, "invalid-client-id", "invalid-client-secret", "http://localhost"
        )
        token = invalid_meeting.test_auth()
        self.assertFalse(token, "Authentication should fail with invalid credentials.")
        print("Invalid token correctly handled.")


if __name__ == "__main__":
    unittest.main()
