# Use Python as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create json folder
RUN mkdir -p /json && chmod 777 /json

# Copy main Python code into the container
COPY main.py .

# By default, main.py runs when the container starts
CMD ["python", "main.py"]