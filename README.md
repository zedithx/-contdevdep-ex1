# Containerized Service Assignment

This project consists of two services running in separate Docker containers that demonstrate containerized microservices communication. The services collect container-specific information such as IP address, running processes, disk space, and uptime. One service exposes an HTTP server to provide this data externally, while the other remains hidden but provides internal data to the first service. Both services should startup and stop together via docker compose.

## Project Structure

- **Service 1**: Hidden HTTP server on port `8199`, collects and exposes its own container information as well as data from Service 2 to the Nginx Webserver.
- **Service 2**: Runs privately within the Docker network and provides its container information to Service 1 when requested.
- **Nginx Service**: Acts as a webserver on the exposed port `8081` 

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
  
- **Service 2**:
  - Collects the same container information but is only accessible by **Service 1** over an internal network.
  - Does not expose any public port.

- **Nginx Service**:
  - Starts webserver on port 8081
  - Retrieves data from appropriate service 1 in round robin fashion on "REQUEST" button 
  - Shuts down system and containers on the "STOP" button

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- Basic understanding of Docker, containers, and HTTP.

## Setup

username: user1
password: Password1

1. **Clone the repository**:
   ```bash
   git clone https://your-repository-url
   cd your-repository-folder
    ```
2. **Build and start the containers up via docker-compose**:
    ```bash
    docker-compose up --build
    ```
3. **Make a curl request to service 1 exposed on port 8199**
    ```bash
    curl http://localhost:8199
    ```
4. **View the returned information of both service containers** <br></br>
5. **You can double check to see if service 2 on port 8080 is exposed publicly. You should not be able to access it**