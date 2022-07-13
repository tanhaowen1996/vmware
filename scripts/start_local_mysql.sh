#!/bin/bash

name=mysql

db_user=cmpvmware
db_pass=notpassword
db_name=cmpvmware

# docker pull mysql

docker rm -f $name
docker run \
    --name $name \
    -p 3306:3306 \
    -p 33060:33060 \
    -e MYSQL_USER=$db_user \
    -e MYSQL_PASSWORD=$db_pass \
    -e MYSQL_ROOT_PASSWORD=$db_pass \
    -e MYSQL_DATABASE=$db_name \
    -v `pwd`/scripts/mysql:/etc/mysql/conf.d \
    -d mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

