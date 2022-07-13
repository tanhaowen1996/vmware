#!/bin/bash

cd /app

if [ $# -eq 0 ]; then
  echo "Usage: start.sh [PROCESS_TYPE](api/scheduler)"
else
  PROCESS_TYPE=$1
fi

function start_api() {
  echo "Start api..."
  python app/cmd/api/main.py
}

function start_scheduler() {
  echo "Start scheduler..."
  python app/cmd/sync/main.py
}

function main() {
  case "$PROCESS_TYPE" in
    "api")
      start_api
      ;;
    "scheduler")
      start_scheduler
      ;;
    *)
      echo "Usage: start.sh [PROCESS_TYPE](api/scheduler)"
      ;;
  esac
}

main
