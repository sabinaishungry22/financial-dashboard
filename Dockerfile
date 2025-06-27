# Use a lightweight Python base image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Command to run the Flask application (direct execution, not via Flask CLI)
# This uses the app.run() call we put directly in app.py
CMD ["python", "app.py"]