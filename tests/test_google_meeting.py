import unittest
from unittest.mock import patch
from incidentbot.google.meeting import GoogleMeeting


class TestGoogleMeeting(unittest.TestCase):
    def setUp(self):
        # Patch 'settings' globally to replace actual settings with mock settings
        patcher_settings = patch("incidentbot.google.meeting.settings")
        # Patch 'requests.post' globally to intercept all HTTP POST requests made by the code
        patcher_requests = patch("incidentbot.google.meeting.requests.post")

        # Start patches for settings and requests.post
        self.mock_settings = patcher_settings.start()
        self.mock_post = patcher_requests.start()

        # Ensure the patches are cleaned up after each test to avoid side effects
        self.addCleanup(patcher_settings.stop)
        self.addCleanup(patcher_requests.stop)

        # Configure the mock settings with fake values for the OAuth credentials
        self.mock_settings.GOOGLE_CLIENT_ID = "mock_client_id"
        self.mock_settings.GOOGLE_CLIENT_SECRET = "mock_client_secret"
        self.mock_settings.GOOGLE_REFRESH_TOKEN = "mock_refresh_token"

        # Configure the mock for 'requests.post' to return a successful token response by default
        self.mock_post.return_value.status_code = 200
        self.mock_post.return_value.json.return_value = {
            "access_token": "mock_access_token"
        }

        # Initialize the GoogleMeeting instance with a test incident name
        self.incident = "Test Incident"
        self.google_meeting = GoogleMeeting(self.incident)

    def test_generate_token_success(self):
        # Test the generation of an OAuth token when the response is successful
        token = self.google_meeting._GoogleMeeting__generate_token()
        self.assertEqual(token, "mock_access_token")  # Verify the token matches the mock value
        self.mock_post.assert_called_once()  # Ensure 'requests.post' was called once

    def test_generate_token_failure(self):
        # Mock a failed token generation response
        self.mock_post.return_value.status_code = 400
        self.mock_post.return_value.json.return_value = {
            "error": "invalid_request"}

        token = self.google_meeting._GoogleMeeting__generate_token()
        self.assertIsNone(token)  # Token generation should fail and return None
        self.mock_post.assert_called_once()  # Ensure 'requests.post' was called once

    def test_create_meeting_success(self):
        # Mock successful responses for token generation and meeting creation
        self.mock_post.side_effect = [
            # First call for token generation
            unittest.mock.Mock(
                status_code=200, json=lambda: {"access_token": "mock_access_token"}
            ),
            # Second call for meeting creation
            unittest.mock.Mock(
                status_code=200,
                json=lambda: {
                    "conferenceData": {
                        "entryPoints": [
                            {"uri": "https://meet.google.com/mock-meeting"}
                        ]
                    }
                },
            ),
        ]

        meeting_url = self.google_meeting.url
        self.assertEqual(meeting_url, "https://meet.google.com/mock-meeting")  # Verify the meeting URL
        self.assertEqual(self.mock_post.call_count, 2)  # Ensure both token and meeting creation calls were made

    def test_create_meeting_failure(self):
        # Mock a successful token generation but failed meeting creation
        self.mock_post.side_effect = [
            unittest.mock.Mock(
                status_code=200, json=lambda: {"access_token": "mock_access_token"}
            ),
            unittest.mock.Mock(
                status_code=400, json=lambda: {"error": "bad_request"}
            ),
        ]

        meeting_url = self.google_meeting.url
        self.assertIsNone(meeting_url)  # Meeting creation should fail and return None
        self.assertEqual(self.mock_post.call_count, 2)  # Ensure both token and meeting creation calls were made

    def test_auth_success(self):
        # Test that authentication succeeds when token generation is successful
        auth_status = self.google_meeting.test_auth()
        self.assertTrue(auth_status)  # Authentication should succeed
        self.mock_post.assert_called_once()  # Ensure 'requests.post' was called once for token generation

    def test_auth_failure(self):
        # Mock a failed token generation response
        self.mock_post.return_value.status_code = 400
        self.mock_post.return_value.json.return_value = {
            "error": "invalid_request"}

        auth_status = self.google_meeting.test_auth()
        self.assertFalse(auth_status)  # Authentication should fail
        self.mock_post.assert_called_once()  # Ensure 'requests.post' was called once for token generation


if __name__ == "__main__":
    unittest.main()
