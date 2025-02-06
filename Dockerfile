FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . . 

# Ensure templates directory is copied correctly
COPY templates /app/templates

# Expose the port
EXPOSE 5000

# Start Flask app
CMD ["python", "app.py"]