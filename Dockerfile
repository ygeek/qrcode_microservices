FROM python:3.6.3

# Install required packages and remove the apt packages cache when done.

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y nginx supervisor libzbar0 poppler-utils&& \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# setup nginx
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY config/deploy/nginx-app.conf /etc/nginx/sites-available/default

# setup supervisor to run nginx and uwsgi
COPY config/deploy/supervisor-app.conf /etc/supervisor/conf.d/

# COPY requirements.txt and RUN pip install BEFORE adding the rest of your code, this will cause Docker's caching mechanism
# to prevent re-installing (all your) dependencies when you made a change a line or two in your app.
COPY src/requirements.txt /home/docker/code/
RUN pip install -Ur /home/docker/code/requirements.txt

# map code volume to /home/docker/code/
COPY . /home/docker/code/

WORKDIR /home/docker/code/

EXPOSE 80
COPY config/deploy/start.sh /home/docker/start.sh
CMD ["/home/docker/start.sh"]
