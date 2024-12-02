import json
import re

import pytest
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8197"
USERNAME = "user1"
PASSWORD = "Password1"


class TestRequest:
    def test_request(self):
        """
        GET /request
        Similar function as REQUEST-button of the GUI (see instructions for nginx exercise),
        but as a text/plain response to the requester.
        """
        response = requests.get(f"{BASE_URL}/request", auth=HTTPBasicAuth(USERNAME, PASSWORD))
        assert response.status_code == 200
        response_text = response.text
        assert "Service 1" in response_text
        assert "Service 2" in response_text
        assert "IP Address" in response_text
        assert "Processes" in response_text
        assert "Disk Space" in response_text
        assert "Time since last boot" in response_text

        # Extract the IP Address
        ip_address = json.loads(response_text).get("Service 1", {}).get("IP Address", None)

        # Validate the presence of an IP address using regex
        ip_pattern = r"^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$"
        assert re.match(ip_pattern, ip_address), f"Invalid IP Address: {ip_address}"

        # Validate that uptime includes "minutes" or "hours"
        assert "minutes" in response_text or "hours" in response_text, "Uptime not in expected format"