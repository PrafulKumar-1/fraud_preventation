# Start from the official Python base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the FastAPI application code into the container
COPY ./app /app/app

# Command to run the Uvicorn server
# The server will be available on port 10000, which Render uses by default.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]