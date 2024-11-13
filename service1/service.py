import socket
import threading

import docker
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

import requests
import subprocess

import logging

# Configure logging
logging.basicConfig(
    filename='app.log',               # Log file name
    filemode='a',                      # Append mode (use 'w' to overwrite each time)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log format
    level=logging.INFO                 # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/request':
            self.handle_request()
        elif self.path == '/stop':
            self.handle_stop()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_request(self):
        # Define the response code and headers
        resp = requests.get('http://service2:8080/')
        service2_resp = resp.text
        processes = subprocess.check_output("ps -ax", shell=True).decode("utf-8")
        disk_space_output = subprocess.check_output("df -h /", shell=True).decode("utf-8")
        lines = disk_space_output.splitlines()
        columns = lines[1].split()
        disk_space = columns[3]
        uptime = " ".join(subprocess.check_output("uptime -p", shell=True).decode("utf-8").split()[1:])
        container_ip = subprocess.check_output("hostname -I", shell=True).decode("utf-8").strip()

        # Create a plain text response
        response_data = f"IP Address: {container_ip}\n" \
                        f"Processes:\n{processes}" \
                        f"Disk Space: {disk_space}\n" \
                        f"Time since last boot: {uptime}\n"
        self.send_response(200)  # 200 OK status
        self.send_header("Content-type", "text/plain")  # Content type header
        self.end_headers()

        # Write the response body
        response_content = f"Service 1\n{response_data}\nService 2\n{service2_resp}"
        self.wfile.write(response_content.encode("utf-8"))  # Send the response
        time.sleep(2)

    def delayed_self_shutdown(self, container_id):
        # Run the script to stop and remove the container after a delay
        subprocess.Popen(["./stop_self.sh", container_id])

    def handle_stop(self):
        # Send response to client indicating that shutdown is in progress
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Containers all shutdown")

        try:
            client = docker.from_env()
            last_container_id = None

            # Get the hostname or IP of the current container to identify it
            current_instance = socket.gethostname()
            print(f"Current instance ID: {current_instance}")

            # Stop and remove all containers except the current instance
            for container in client.containers.list():
                if "service1" in container.name and container.attrs['Config']['Hostname'] == current_instance:
                    last_container_id = container.id
                    continue
                else:
                    container.stop()
                    container.remove()

            shutdown_thread = threading.Thread(target=self.delayed_self_shutdown(last_container_id))
            shutdown_thread.start()

        except Exception as e:
            error_message = f"Error during shutdown: {e}"
            print(error_message)
            self.wfile.write(error_message.encode("utf-8"))

# Define the server address and port
server_address = ('', 8199)  # Listen on all available IP addresses, port 8199
httpd = HTTPServer(server_address, MyHandler)

print("Serving on port 8199...")
# Start the HTTP server
httpd.serve_forever()