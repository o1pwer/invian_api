# Dockerfile for the sensor
# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./components/sensor /app/components/sensor
ADD ./invian_shared /app/invian_shared
ADD ./components/sensor/requirements.txt /app/components/sensor/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/components/sensor/requirements.txt

# Adjust the PYTHONPATH to include the necessary directories
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/components:/app/invian_shared"

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run main.py when the container launches
CMD ["python", "/app/components/sensor/main.py"]

