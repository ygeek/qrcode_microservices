uwsgi.ini:
- socker文件写入路径：/home/docker/app.sock
- 代码目录：/home/docker/code/app/
- uwsgi模块：mysite.wsgi:application

nginx-app.conf:
- socket文件读取路径： /home/docker/app.sock
- Flask static的URL和文件路径：/static -> /home/docker/volatile/static
- uwsgi配置参数路径：/home/docker/code/config/deploy/uwsgi_params

Supervisor-app.conf:
- uwsgi配置文件路径：/home/docker/code/docker_config/uwsgi.ini
- uwsgi日志路径：/home/docker/app-uwsgi.log
- nginx日志路径：/home/docker/nginx-app.log

