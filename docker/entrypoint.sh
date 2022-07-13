#!/bin/bash
# entrypoint.sh file of Dockerfile

# Section1: Bash options
set -o errexit
set -o pipefail
set -o nounset

# Section2: Health of dependent services
mysql_ready() {
  python << END
import sys

from mysql.connector import connect, Error

try:
    connect(
        database="${DATABASE}",
        host="${DB_HOST}",
        port="${DB_PORT}",
        user="${DB_USER}",
        password="${DB_PASSWORD}",
    )
except Error as e:
    print(e)
    sys.exit(-1)
END
}

until mysql_ready; do
  >&2 echo "Waiting for MySQL to become available..."
  sleep 5
done
>&2 echo "MySQL is available"

# Section3: DB migrations
alembic upgrade head

exec start.sh "$@"
