import requests
from flask import Flask, request, jsonify
import logging
import docker
import subprocess
import socket
import threading
import time

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename='status.log',
    filemode='a',
    format='%(asctime)s: %(message)s',
    level=logging.INFO
)

# Global state
state = "INIT"
state_log = []
logged_in = False


@app.route('/state', methods=['PUT'])
def update_state():
    global state, state_log

    # Read the new state from the request body
    new_state = request.data.decode('utf-8')
    logging.info(f"Received state change request: {new_state}")

    # Validate the new state
    if new_state not in ["INIT", "PAUSED", "RUNNING", "SHUTDOWN"]:
        return jsonify({"error": "Invalid state"}), 400

    # Update the state
    if new_state != state:
        state_log.append(f"{state} -> {new_state}")
        logging.info(f"State transition: {state} -> {new_state}")
        state = new_state

        # Handle state-specific actions
        if new_state == "SHUTDOWN":
            handle_stop()
        elif new_state == "INIT":
            reset_to_initial()

        return jsonify({"message": f"State updated to {state}"}), 200
    else:
        return jsonify({"message": "No change in state"}), 200


@app.route('/state', methods=['GET'])
def get_state():
    """
    GET /state
    Returns the current state.
    """
    return jsonify({"state": state}), 200


@app.route('/run-log', methods=['GET'])
def get_run_log():
    """
    GET /run-log
    Returns the state transition log.
    """
    return jsonify({"log": state_log}), 200


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


def handle_stop():
    """
    Shuts down all containers except the current one.
    """
    logging.info("Handling system shutdown...")
    try:
        client = docker.from_env()
        current_instance = socket.gethostname()
        last_container_id = None

        for container in client.containers.list():
            if "service1" in container.name and container.attrs['Config']['Hostname'] == current_instance:
                last_container_id = container.id
                continue
            else:
                container.stop()
                container.remove()

        # Schedule self-shutdown
        threading.Thread(target=delayed_self_shutdown, args=(last_container_id,)).start()
        logging.info("Containers shut down.")
    except Exception as e:
        logging.error(f"Error during shutdown: {str(e)}")


def reset_to_initial():
    """
    Resets the system to its initial state.
    """
    global logged_in
    logged_in = False
    logging.info("System reset to INIT state.")


def delayed_self_shutdown(container_id):
    """
    Delays shutting down the current container.
    """
    time.sleep(2)
    subprocess.Popen(["./stop_self.sh", container_id])


# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8199)