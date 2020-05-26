# Use official Python image
# https://hub.docker.com/_/python
FROM python:3.8

# Install missing libs manually
RUN apt-get update
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils

# Install Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy local code to container image
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

# Run gunicorn webserver on container startup
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app