#!/bin/sh

# 这是一个djapp启动脚本示例， 请自定义该脚本

echo "run MODE: $SERVICE_MODE"

if [ "cworker" = "$SERVICE_MODE" ]; then
    celery -A djapp worker -E -Ofair -lINFO -f /dev/null
elif [ "cbeat" = "$SERVICE_MODE" ]; then
    celery -A djapp beat
elif [ "gunicorn" = "$SERVICE_MODE" ]; then
    gunicorn djapp.wsgi -w 5 -b :18002
elif [ "django" = "$SERVICE_MODE" ]; then
    ./manage.py runserver 18002
elif [ "flower" = "$SERVICE_MODE" ]; then
    celery -A djapp flower --address=0.0.0.0 --port=5552
else
    echo "unknown mode: $SERVICE_MODE"
fi
