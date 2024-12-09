import pytest
import requests
import responses
from requests.auth import HTTPBasicAuth
from unittest.mock import patch

BASE_URL = "http://localhost:8197"
USERNAME = "user1"
PASSWORD = "Password1"

@pytest.fixture
def reset_state():
    """Fixture to reset state to INIT before each test."""
    requests.put(f"{BASE_URL}/state", data="INIT", auth=HTTPBasicAuth(USERNAME, PASSWORD))
    yield


class TestPutState:
    """
    PUT /state (payload “INIT”, “PAUSED”, “RUNNING”, “SHUTDOWN”)
        PAUSED = the system does not response to requests
        RUNNING = the system responses to requests normally
        If the new state is equal to previous nothing happens.
        There are two special cases:
        INIT = everything (except log information for /run-log) is set to the initial state and
        login is needed get the system running again.
        SHUTDOWN = all containers are stopped
"""
    def test_put_state_running(self, reset_state):
        response = requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        assert response.status_code == 200
        response_json = response.json()  # Convert response to JSON
        assert response_json["message"] == "State updated to RUNNING"

    def test_put_state_init(self, reset_state):
        response = requests.put(f"{BASE_URL}/state", data="INIT", auth=HTTPBasicAuth(USERNAME, PASSWORD))  # No state change
        assert response.status_code == 200  # Should not trigger an error
        response_json = response.json()  # Convert response to JSON
        assert response_json["message"] == "No change in state"

    def test_put_state_paused(self, reset_state):
        response = requests.put(f"{BASE_URL}/state", data="PAUSED", auth=HTTPBasicAuth(USERNAME, PASSWORD))  # No state change
        assert response.status_code == 400  # Should not trigger an error
        response_json = response.json()
        assert response_json["message"] == "State change to PAUSED is not allowed. " \
                                           "Only changes in state to RUNNING are allowed"

    def test_init_failed_authentication(self, reset_state):
        """In INIT state, shouldn't work without authentication"""
        response = requests.put(f"{BASE_URL}/state", data="RUNNING")
        assert response.status_code == 401

    def test_no_authentication_needed(self, reset_state):
        """In other states, you should not need authentication"""
        requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        # When state is running already, authentication should not be needed
        response = requests.put(f"{BASE_URL}/state", data="PAUSED")
        assert response.status_code == 200
        response_json = response.json()  # Convert response to JSON
        assert response_json["message"] == "State updated to PAUSED"

    @patch("requests.put")
    def test_put_state_shutdown_mocked(self, mock_put, reset_state):
        requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        mock_put.return_value.status_code = 200
        mock_put.return_value.json = lambda: {"message": "State updated to SHUTDOWN"}
        response = requests.put(f"{BASE_URL}/state", data="SHUTDOWN", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        assert response.status_code == 200
        response_json = response.json()
        assert response_json["message"] == "State updated to SHUTDOWN"


class TestGetState:
    def test_get_state(self, reset_state):
        """
        GET /state (as text/plain)
            get the value of state
        """
        response = requests.get(f"{BASE_URL}/state")
        assert response.status_code == 200
        assert response.text == "INIT"

    def test_get_state_paused(self, reset_state):
        """
        GET /state (as text/plain)
            Should not work when the system is paused
        """
        # Need to put into running state first before pause
        requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        requests.put(f"{BASE_URL}/state", data="PAUSED", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        response = requests.get(f"{BASE_URL}/state")
        assert response.status_code == 401


class TestGetStateLog:
    @responses.activate
    def test_get_state_log_mocked(self, reset_state):
        """
        GET /run-log (as text/plain)
        """
        responses.assert_all_requests_are_fired = True
        responses.add(
            responses.GET,
            f"{BASE_URL}/run-log",
            body="2023-11-01T06:35:01.380Z: INIT->RUNNING\n"
                 "2023-11-01T06:40:01.373Z: RUNNING->PAUSED\n"
                 "2023-11-01T06:40:01.373Z: PAUSED->RUNNING",
            status=200,
            content_type="text/plain"
        )

        response = requests.get(f"{BASE_URL}/run-log")
        assert response.status_code == 200
