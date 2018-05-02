#! /bin/bash
docker exec -it qrcode_backend uwsgi --reload /tmp/uwsgi.pid
