#! /bin/bash
cd /home/docker/code/src/
mkdir -p /var/logs/
touch /var/logs/
supervisord -n

