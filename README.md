# Containerized Service Final Project

This project implements a containerized multi-service application extended with a CI/CD pipeline. It includes an API Gateway, monitoring, and a test-driven development approach.
Both services are written in different languages to demonstrate the capabilities of microservices.

## Project Overview

- **Service 1**: Provides container-specific data and integrates with **Service 2**. Written in Python.
- **Service 2**: Operates privately within the Docker network, supplying data to **Service 1**. Written in Ruby.
- **API Gateway**: 
  - Extended NGINX, functioning as a reverse proxy, load balancer, and API Gateway.
  - Exposes REST APIs for system state management and monitoring.

## Features

### Core Features
1. **Container Information**:
   - IP Address
   - Running Processes (`ps -ax`)
   - Available Disk Space (`df -h`)
   - Uptime (`uptime -p`)
2. **System States**:
   - `INIT`: Resets application to default state.
   - `RUNNING`: Processes requests normally.
   - `PAUSED`: Suspends request handling.
   - `SHUTDOWN`: Stops all containers.
3. **API Endpoints**:
   - `PUT /state`: Transition system state.
   - `GET /state`: Retrieve current state.
   - `GET /request`: Perform load-balanced service requests.
   - `GET /run-log`: Fetch state change logs.
4. **Monitoring**:
   - Displays service start time and request count since startup.
5. **Web Interface**:
   - Allows users to make the API calls on a GUI

### CI/CD Pipeline
1. **GitLab CI**:
   - Configured with `.gitlab-ci.yml` for Build, Test, and Deploy stages.
2. **Test-Driven Development**:
   - Tests implemented prior to feature development.
   - Tests stored in `tests/` directory.
3. **Pipeline Execution**:
   - Automatically builds and deploys upon code pushes.

### Optional Features Implemented
- Static analysis tool - `pylint`.
- Deployment to a virtual machine for external testing.

## Prerequisites
- **Docker** and **Docker Compose** installed.
- GitLab Runner registered and configured (if testing CI/CD pipeline)
- Tools like `curl` or `Postman` for testing API endpoints.
- Basic knowledge of CI/CD workflows and Docker.

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone -b project https://github.com/zedithx/contdevdep-ex
   cd contdevdep-ex
   ```

2. **Build and start containers**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Using the WebUI**
  1. Open up the webpage served by Nginx on localhost:8197
  2. Enter the authentication details based on the login.txt
  3. You can now test the request button which will populate the text area with service 1 & service 2 response
  4. You can also test the stop button which stops all containers
  5. These requests to service1 are handled in a round robin fashion by the nginx server as a load balancer


4. **Calling the endpoints**

**Note: Running in test environment to test locally**
Run this command instead. It saves data to a temporary volume instead.
```bash
docker-compose -f docker-compose.test.yml up -d
pytest
```

Please view the end report in the repository for more information and learning points
