"""
This module contains the api endpoints to serve changes of state or getting of states
"""
import os

import logging
import subprocess
import requests

from flask import Flask, request, jsonify, make_response, Response
from utils.state_management import StateChange
from utils.time_format import format_log_entry

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s: %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # Log to stdout
        logging.FileHandler("status.log") # Log to my status.log file
    ]
)

# maps what states a state can transition into, shutdown not needed as its a final state
STATE_DICT = {"INIT": ["RUNNING"], "RUNNING": ["INIT", "PAUSED", "SHUTDOWN"],
              "PAUSED": ["INIT", "PAUSED", "SHUTDOWN"]}

@app.route('/check_pause', methods=['GET'])
def check_pause():
    """Checks if the system is in paused state. if it is, all requests should not go through"""
    state_file_path = "/shared-data/state.txt"
    # Read the current state from the volume
    if not os.path.exists(state_file_path):
        logging.info("Making state file...")
        with open(state_file_path, "a", encoding="utf-8"):
            pass  # Create the file if it does not exist
        state = "INIT"

    else:
        with open(state_file_path, "r", encoding="utf-8") as f:
            state = f.read()
            if not state:
                state = "INIT"
    if state == "PAUSED":
        return Response(status=401)  # Authorized
    return Response(status=200)  # Forbidden

@app.route('/check_state', methods=['GET'])
def check_state():
    """Check if the state is INIT. If state is init when attempting to
    change state, auth is required"""
    state_file_path = "/shared-data/state.txt"
    # Read the current state from the volume
    if not os.path.exists(state_file_path):
        logging.info("Making state file...")
        with open(state_file_path, "a", encoding="utf-8"):
            pass  # Create the file if it does not exist
        state = "INIT"

    else:
        with open(state_file_path, "r", encoding="utf-8") as f:
            state = f.read()
            if not state:
                state = "INIT"
    if state == "INIT":
        auth = request.authorization
        if not auth or not (auth.username == "user1" and auth.password == "Password1"):
            return Response("Unauthorized", status=401)
    return Response("OK", status=200)

@app.route('/state', methods=['PUT'])
def update_state():
    """
    PUT /state
    Makes request to change the state of machine.
    PAUSED = the system does not response to requests
    INIT = need login to change state from this
    RUNNING = Respond to requests normally
    SHUTDOWN = Shutdown containers
    """
    # Define file paths in the shared volume
    state_file_path = "/shared-data/state.txt"
    state_log_file_path = "/shared-data/state_log.txt"

    # Read the new state from the request body
    logging.info(request.data)
    new_state = request.data.decode('utf-8')

    # Validate the new state
    if new_state not in ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]:
        return jsonify({"error": new_state}), 400

    # Read the current state from the volume
    if not os.path.exists(state_file_path):
        logging.info("Making state file...")
        with open(state_file_path, "a", encoding="utf-8"):
            pass  # Create the file if it does not exist
        state = "INIT"

    else:
        with open(state_file_path, "r", encoding="utf-8") as f:
            state = f.read()
            if not state:
                state = "INIT"

    # Update the state if it has changed
    if new_state != state:
        if new_state not in STATE_DICT[state]:
            return jsonify({"message": f"State change to {new_state} is not allowed. "
                                       f"Only changes in state to {','.join(STATE_DICT[state])}"
                                       f" are allowed"}), 400

        # Ensure the state log file exists
        if not os.path.exists(state_log_file_path):
            with open(state_log_file_path, "a", encoding="utf-8") as log_file:
                pass  # Create the file if it does not exist

        # Update the state log
        log_entry = format_log_entry(state, new_state)
        with open(state_log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry + "\n")

        # Update the state file
        with open(state_file_path, "w", encoding="utf-8") as state_file:
            state_file.write(new_state)

        # Perform state-specific actions
        # SHUTDOWN
        if new_state == "SHUTDOWN":
            state_handler = StateChange()
            state_handler.handle_stop()
        # If future handlers, put here

        return jsonify({"message": f"State updated to {new_state}"}), 200
    return jsonify({"message": "No change in state"}), 200


@app.route('/state', methods=['GET'])
def get_state():
    """
    GET /state
    Returns the current state as plain text.
    """
    state_file_path = "/shared-data/state.txt"
    # Read the state from the file
    with open(state_file_path, "r", encoding="utf-8") as state_file:
        state = state_file.read().strip()  # Remove any trailing newlines or spaces
        if not state:
            state = "INIT"
    # Log the state
    logging.info("Current state: %s", state)

    # Return the state as plain text
    response = make_response(state)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/run-log', methods=['GET'])
def get_run_log():
    """
    GET /run-log
    Returns the state transition log as plain text.
    """
    # Convert the log (list) to a plain text string
    state_log_file_path = "/shared-data/state_log.txt"
    with open(state_log_file_path, "r", encoding="utf-8") as state_log_file:
        state_log = state_log_file.read()  # Remove any trailing newlines or spaces
        if not state_log:
            state_log = "There is no state log yet. No changes were made to the state" \
                        " since the uptime of the service"
    return state_log, 200, {'Content-Type': 'text/plain'}


@app.route('/request', methods=['GET'])
def handle_request():
    """
    GET /request
    Simulates a request to fetch system details and information from another service.
    """
    try:
        # Simulate a request to another service
        service2_response = requests.get('http://service2:8080/', timeout=5).text

        # Gather system information
        processes = subprocess.check_output("ps -ax", shell=True)\
            .decode("utf-8")
        disk_space = subprocess.check_output("df -h /", shell=True)\
        .decode("utf-8").splitlines()[1].split()[3]
        uptime = subprocess.check_output("uptime -p", shell=True).decode("utf-8").strip()
        container_ip = subprocess.check_output("hostname -I", shell=True).decode("utf-8").strip()

        response_data = {
            "Service 1": {
                "IP Address": container_ip,
                "Processes": processes,
                "Disk Space": disk_space,
                "Uptime": uptime
            },
            "Service 2": service2_response
        }
        return jsonify(response_data), 200

    except requests.exceptions.RequestException as e:
        logging.error("Network error in /request: %s", str(e))
        return jsonify({"error": "Failed to contact Service 2"}), 502

    except subprocess.CalledProcessError as e:
        logging.error("Subprocess error: %s", str(e))
        return jsonify({"error": "Failed to execute system command"}), 500

    except Exception as e:          # pylint: disable=broad-exception-caught
        # Exclude specific system-level exceptions
        if isinstance(e, (SystemExit, KeyboardInterrupt)):
            raise
        # Log and respond for other unexpected exceptions
        logging.error("Unexpected error in /request: %s", str(e))
        return jsonify({"error": "An unexpected error occurred"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)
