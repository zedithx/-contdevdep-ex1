# define python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# copy the current directory contents into container
COPY . /app

# Install system dependencies for 'ps' and 'df' commands
RUN apt-get update && apt-get install -y --no-install-recommends procps

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8199 available to the world outside this container
EXPOSE 8199

# Run app.py when the container launches
CMD ["python", "service.py"]

