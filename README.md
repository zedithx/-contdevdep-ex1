# Containerized Service Assignment

This project sets up a multi-container application using Docker and Docker Compose, featuring an NGINX web server for
load balancing and reverse proxying, containerized services, and network configurations.

## Project Structure

- **Service 1**: Hidden HTTP server on port `8199`, collects and exposes its own container information as well as data from Service 2 to the Nginx Webserver.
- **Service 2**: Runs privately within the Docker network and provides its container information to Service 1 when requested.
- **Nginx Service**: Acts as a webserver, reverse proxy and load balancer on the exposed port `8081` 

### Features

- Both services collect the following container-specific information:
  - **IP Address**
  - **Running Processes** (`ps -ax`)
  - **Available Disk Space** (`df -h`)
  - **Time Since Last Boot** (`uptime -p`)
  
- **Service 1**:
  - 3 Instances to be load balanced
  - Runs a HTTP server on inner port `8199` to serve its own container data.
  - Requests and displays information from **Service 2**.
  - Helps to stop the containers from running and exit system on "STOP" button
  
- **Service 2**:
  - Collects the same container information but is only accessible by **Service 1** over an internal network.
  - Does not expose any public port.

- **Nginx Service**:
  - Starts webserver on the only exposed port 8081
  - Retrieves data from appropriate service 1 in round robin fashion on "REQUEST" button 
  - Shuts down system and containers on the "STOP" button

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- Basic understanding of Docker, containers, and HTTP.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://your-repository-url
   cd your-repository-folder
    ```
2. **Build and start the containers up via docker-compose**:
    ```bash
    docker-compose up --build
    ```
3. **Open up the webpage served by Nginx on localhost:8081**
4. **Enter the authentication details based on the login.txt**
5. **You can now test the request button which will populate the text area with service 1 & service 2 response**
6. **You can also test the stop button which stops all containers**
7. **These requests to service1 are handled in a round robin fashion by the nginx server as a load balancer**