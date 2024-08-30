FROM python:3.11

WORKDIR /app

# Copy application files
COPY . /app

# Install ffmpeg and other dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r needs.txt

# Expose the port if necessary (assuming you have a FastAPI or similar web service running)
EXPOSE 8080

# Add a cleanup mechanism (optional if needed)
# This will run a cleanup script that you can add to your project
# For example: a script that deletes old files
# COPY cleanup.sh /app/cleanup.sh
# RUN chmod +x /app/cleanup.sh

# Start the application
CMD ["python", "main.py"]
