# Use the official Python 3.11 image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy everything from the current directory to /app in the container,
# excluding the 'exploration' file using .dockerignore
COPY . .

# Ensure 'exploration' is excluded (create a .dockerignore file)
RUN rm -f /app/exploration

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

