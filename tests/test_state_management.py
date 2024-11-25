import pytest
import requests
from requests.auth import HTTPBasicAuth

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
        assert response_json["message"] == "State updated to INIT"

    def test_put_state_paused(self, reset_state):
        response = requests.put(f"{BASE_URL}/state", data="PAUSED", auth=HTTPBasicAuth(USERNAME, PASSWORD))  # No state change
        assert response.status_code == 200  # Should not trigger an error
        response_json = response.json()
        assert response_json["message"] == "State updated to PAUSED"

    def test_failed_authentication(self, reset_state):
        response = requests.put(f"{BASE_URL}/state", data="RUNNING")
        assert response.status_code == 401

    def test_put_state_shutdown(self, reset_state):
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
        response = requests.get(f"{BASE_URL}/state", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        assert response.status_code == 200
        assert response.text == "INIT"

    def test_get_state_log(self, reset_state):
        """
        GET /run-log (as text/plain)
        Get information about state changes
        Example response:
        2023-11-01T06.35:01.380Z: INIT->RUNNING
        2023-11-01T06:40:01.373Z: RUNNING->PAUSED
        2023-11-01T06:40:01.373Z: PAUSET->RUNNING
        """
        requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        requests.put(f"{BASE_URL}/state", data="PAUSED", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        requests.put(f"{BASE_URL}/state", data="RUNNING", auth=HTTPBasicAuth(USERNAME, PASSWORD))

        # Get the run-log
        response = requests.get(f"{BASE_URL}/run-log", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        assert response.status_code == 200

        # Validate log entries
        run_log = response.text.splitlines()
        assert len(run_log) == 3
        assert "INIT->RUNNING" in run_log[0]
        assert "RUNNING->PAUSED" in run_log[1]
        assert "PAUSED->RUNNING" in run_log[2]
