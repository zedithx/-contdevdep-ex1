# define python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# copy the current directory contents into container
COPY . /app

RUN chmod +x /app/stop_self.sh

# Install system dependencies for 'ps' and 'df' commands
RUN apt-get update && apt-get install -y docker.io procps

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip list

# Run app.py when the container launches
CMD ["python", "service.py"]

