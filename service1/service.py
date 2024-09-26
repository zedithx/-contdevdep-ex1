from http.server import SimpleHTTPRequestHandler, HTTPServer

import requests
import subprocess

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
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


# Define the server address and port
server_address = ('', 8199)  # Listen on all available IP addresses, port 8080
httpd = HTTPServer(server_address, MyHandler)

print("Serving on port 8199...")
# Start the HTTP server
httpd.serve_forever()