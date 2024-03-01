# Use an official Python runtime as a base image
FROM python:3.9-slim

# Install SQLite3
RUN apt-get update && apt install -y sqlite3 libsqlite3-dev && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run initialize.py when the container launches
CMD ["python", "initialize.py"]
