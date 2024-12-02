import os

import requests
import logging
import subprocess

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

@app.route('/check_pause', methods=['GET'])
def check_pause():
    # Example: Check Authorization header
    state_file_path = "/shared-data/state.txt"
    # Read the current state from the volume
    if not os.path.exists(state_file_path):
        logging.info("Making state file...")
        with open(state_file_path, "a") as state_file:
            pass  # Create the file if it does not exist
        state = "INIT"

    else:
        with open(state_file_path, "r") as f:
            state = f.read()
            if not state:
                state = "INIT"
    if state == "PAUSED":
        return Response(status=401)  # Authorized
    return Response(status=200)  # Forbidden

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
        with open(state_file_path, "a") as state_file:
            pass  # Create the file if it does not exist
        state = "INIT"

    else:
        with open(state_file_path, "r") as f:
            state = f.read()
            if not state:
                state = "INIT"

    # Update the state if it has changed
    if new_state != state:
        # Ensure the state log file exists
        if not os.path.exists(state_log_file_path):
            with open(state_log_file_path, "a") as log_file:
                pass  # Create the file if it does not exist

        # Update the state log
        log_entry = format_log_entry(state, new_state)
        with open(state_log_file_path, "a") as log_file:
            log_file.write(log_entry + "\n")

        # Update the state file
        with open(state_file_path, "w") as state_file:
            state_file.write(new_state)

        # Perform state-specific actions
        # SHUTDOWN
        if new_state == "SHUTDOWN":
            state_handler = StateChange()
            state_handler.handle_stop()
        # INIT
        elif new_state == "INIT":
            state_handler = StateChange()
            state_handler.handle_init()
        # RUNNING
        elif new_state == "RUNNING":
            pass
        # PAUSED
        else:
            pass

        return jsonify({"message": f"State updated to {new_state}"}), 200
    else:
        return jsonify({"message": "No change in state"}), 200


@app.route('/state', methods=['GET'])
def get_state():
    """
    GET /state
    Returns the current state as plain text.
    """
    state_file_path = "/shared-data/state.txt"
    # Read the state from the file
    with open(state_file_path, "r") as state_file:
        state = state_file.read().strip()  # Remove any trailing newlines or spaces
        if not state:
            state = "INIT"
    # Log the state
    logging.info(f"Current state: {state}")

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
    with open(state_log_file_path, "r") as state_log_file:
        state_log = state_log_file.read()  # Remove any trailing newlines or spaces
        if not state_log:
            state_log = "There is no state log yet. No changes were made to the state since the uptime of the service"
    return state_log, 200, {'Content-Type': 'text/plain'}


@app.route('/request', methods=['GET'])
def handle_request():
    """
    GET /request
    Simulates a request to fetch system details and information from another service.
    """
    try:
        # Simulate a request to another service
        service2_response = requests.get('http://service2:8080/').text

        # Gather system information
        processes = subprocess.check_output("ps -ax", shell=True).decode("utf-8")
        disk_space = subprocess.check_output("df -h /", shell=True).decode("utf-8").splitlines()[1].split()[3]
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
    except Exception as e:
        logging.error(f"Error in /request: {str(e)}")
        return jsonify({"error": "Failed to fetch data"}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)