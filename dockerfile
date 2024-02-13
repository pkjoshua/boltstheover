# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set display port as an environment variable
ENV DISPLAY=:99

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

# Install utilities
RUN apt update && apt install -y wget gnupg2 unzip \
    # Install Chrome
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb; apt -fy install \
    # Download a specific version of ChromeDriver
    && wget -q https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chrome-headless-shell-linux64.zip \
    && unzip chrome-headless-shell-linux64.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chrome-headless-shell-linux64 \
    && rm google-chrome-stable_current_amd64.deb chrome-headless-shell-linux64.zip \
    # Clean up
    && apt clean && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Run the command to start uWSGI
CMD ["python3", "initialize.py"]
