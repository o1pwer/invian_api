# Dockerfile
FROM python:3.9

WORKDIR /app

# We copy just the requirements.txt first to leverage Docker cache
COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:."