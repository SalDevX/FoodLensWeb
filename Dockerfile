# syntax=docker/dockerfile:1

# Use the specific Python version you need
ARG PYTHON_VERSION=3.13.3

FROM python:${PYTHON_VERSION}-slim

# Label to identify Fly.io runtime
LABEL fly_launch_runtime="flask"

# Set working directory inside container
WORKDIR /code

# Install required Python dependencies
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all the files into the container
COPY . .

# Set Flask environment variables for production
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080

# Expose the port Flask will run on
EXPOSE 8080



# Run the Flask application
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080" ]








