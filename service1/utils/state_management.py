"""
This module contains a class function that holds the handler for state changes used in the apis
"""
import socket
import threading
import time
import subprocess
import logging
import docker

class StateChange:
    """ This class contains handlers for the STOP state"""
    def __init__(self):
        self.client = docker.from_env()

    # STOP handler
    def handle_stop(self):
        """
        Shuts down all containers except the current one. Set the state back to init
        after shutdown success
        """
        state_file_path = "/shared-data/state.txt"
        logging.info("Handling system shutdown...")
        try:
            # Get the hostname of the current container
            current_instance = socket.gethostname()
            logging.info("Current instance hostname: %s", current_instance)

            last_container_id = None

            # Stop and remove all containers except the current one
            for container in self.client.containers.list():
                if "service1" in container.name and \
                        container.attrs['Config']['Hostname'] == current_instance:
                    last_container_id = container.id
                    continue
                logging.info("Stopping container: %s", container.name)
                container.stop()
                logging.info("Removing container: %s", container.name)
                container.remove()


            if last_container_id:
                # Schedule self-shutdown
                shutdown_thread = threading.Thread(
                    target=self.delayed_self_shutdown, args=(last_container_id,)
                )
                shutdown_thread.start()
            # Lastly, set the state back to INIT
            with open(state_file_path, "w", encoding="utf-8") as state_file:
                state_file.write("INIT")

            logging.info("All containers shut down successfully.")
        except socket.error as e:
            logging.error("Socket error: %s", str(e))

    @staticmethod
    def delayed_self_shutdown(container_id):
        """
        Delays shutting down the current container.
        """
        try:
            logging.info("Delaying self-shutdown for 2 seconds...")
            time.sleep(2)
            # Use subprocess to run the shutdown script
            subprocess.Popen(["./stop_self.sh", container_id])  # pylint: disable=consider-using-with
            logging.info("Initiated self-shutdown for container ID: %s", container_id)
        except (OSError, subprocess.SubprocessError) as e:  # Catch specific exceptions
            logging.error("Error during shutdown: %s", str(e))
