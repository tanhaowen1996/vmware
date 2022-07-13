#!/bin/bash

docker run -it --rm mysql \
  mysql -h `ifconfig en0 | awk '/inet /{print $2}'` -ucmpvmware -pnotpassword

