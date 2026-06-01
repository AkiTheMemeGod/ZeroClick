# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements-deploy.txt

# Create necessary directories
RUN mkdir -p data downloads logs web

# Ensure database is initialized (it will handle JSON import if empty)
# EXPOSE 8000

# Run the web service on container startup.
# We use gunicorn with a uvicorn worker for production performance.
CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app.main:app
