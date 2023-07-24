# Dockerfile for the sensor
# Use an official Python runtime as a parent image
FROM invian_shared

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD ./components/sensor /app
ADD ./invian_shared /app/invian_shared

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Adjust the PYTHONPATH to include the necessary directories
ENV PYTHONPATH "${PYTHONPATH}:/app:/app/invian_shared"

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]

