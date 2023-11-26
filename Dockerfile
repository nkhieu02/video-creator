# Use an official Python runtime as a parent image
FROM python:3.9.18-slim-bullseye as install-packages

# Set environment variable to suppress pip user warnings
ENV PIP_ROOT_USER_ACTION=ignore

# Create and set the working directory
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY ./requirements.txt ./requirements.txt

# Install any needed packages specified in requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt

# Build the video-creator image
FROM install-packages AS video-creator

# Create a non-root user and set ownership of the app directory
RUN useradd -ms /bin/bash video-creator \
    && chown -R video-creator:video-creator /usr/src/app

# Switch to the non-root user
USER video-creator

# Copy the current directory contents into the container at /usr/src/app
COPY --chown=video-creator:video-creator ./ ./

# Expose port 8000 for the application
EXPOSE 8000

# Specify the command to run on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
