import logging
import docker
import socket
import threading
import time
import subprocess


class StateChange:
    def __init__(self):
        self.client = docker.from_env()

    # STOP handler
    def handle_stop(self):
        """
        Shuts down all containers except the current one.
        """
        logging.info("Handling system shutdown...")
        try:
            # Get the hostname of the current container
            current_instance = socket.gethostname()
            logging.info(f"Current instance hostname: {current_instance}")

            last_container_id = None

            # Stop and remove all containers except the current one
            for container in self.client.containers.list():
                if "service1" in container.name and container.attrs['Config']['Hostname'] == current_instance:
                    last_container_id = container.id
                    continue
                else:
                    logging.info(f"Stopping container: {container.name}")
                    container.stop()
                    logging.info(f"Removing container: {container.name}")
                    container.remove()

            if last_container_id:
                # Schedule self-shutdown
                shutdown_thread = threading.Thread(
                    target=self.delayed_self_shutdown, args=(last_container_id,)
                )
                shutdown_thread.start()

            logging.info("All containers shut down successfully.")
        except Exception as e:
            logging.error(f"Error during shutdown: {str(e)}")

    @staticmethod
    def delayed_self_shutdown(container_id):
        """
        Delays shutting down the current container.
        """
        try:
            logging.info("Delaying self-shutdown for 2 seconds...")
            time.sleep(2)
            # Use subprocess to run the shutdown script
            subprocess.Popen(["./stop_self.sh", container_id])
            logging.info(f"Initiated self-shutdown for container ID: {container_id}")
        except Exception as e:
            logging.error(f"Error during self-shutdown: {str(e)}")

    # INIT handler
    def reset_to_initial(self):
        """
        Resets the system to its initial state.
        """
