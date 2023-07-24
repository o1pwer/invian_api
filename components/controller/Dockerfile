# Dockerfile for the controller
# Use an official Python runtime as a parent image
FROM python:3.8

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./components/controller /app/controller
ADD ./invian_shared /app/invian_shared
ADD ./components/controller/requirements.txt /app/controller/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /app/controller/requirements.txt

# Adjust the PYTHONPATH to include the necessary directories
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/controller:/app/invian_shared"

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "/app/controller/main.py"]