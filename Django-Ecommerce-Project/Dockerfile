# Use the official Python runtime image
FROM python:3.8-slim

# Creating an app directory
RUN mkdir /app

# Set the working directory in the Django project

WORKDIR /app

# prevent python for storing the byte code (*.pyc) files in the docker disk!
ENV PYTHONDONTWRITEBYTECODE=1

# prevents python for buffering stdout and stderr
ENV PYTHONBUFFERED=1

# Upgrade pip
RUN pip install --upgrade pip 


# Now copy the Django project requirements.tx file.
COPY requirements.txt /app


# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt


# Now  and folders into the app working directory in docker container.
COPY . /app/

# Expose the Django port
EXPOSE 8000

