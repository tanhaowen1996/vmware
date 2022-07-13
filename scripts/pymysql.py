#!/usr/bin/env python3

from getpass import getpass
from mysql.connector import connect, Error

db_host = "10.67.85.128"
db_port = 3306
db_user = "cmpvmware"
db_pass = "notpassword"
db_name = "cmpvmware"

try:
    with connect(
        database=db_name,
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        # auth_plugin='mysql_native_password',
    ) as connection:
        print(connection)
except Error as e:
    print(e)
