# usage: docker build -t lalert:IMAGE_VERSION .
FROM registry-itwork.yonghui.cn/library/python:3.8-alpine3.11

# 请自定义以下内容

MAINTAINER YH
ENV LANG en_US.UTF-8
RUN echo $'http://mirrors.aliyun.com/alpine/v3.11/main\n\
http://mirrors.aliyun.com/alpine/v3.11/community' > /etc/apk/repositories
RUN apk --update add alpine-sdk \
        musl-dev \
        libffi-dev \
        postgresql-dev \
        ack \
        busybox-extras \
        net-tools \
        tcptraceroute \
        vim \
        zlib \
        jpeg-dev \
        zlib-dev \
        tzdata
ENV TZ Asia/Shanghai
RUN ln -s -f /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone
ENV opt /opt
WORKDIR ${opt}
ADD . .
RUN pip3 install -U -i https://mirrors.aliyun.com/pypi/simple/ pip

CMD ["/bin/sh", "runserver.sh"]

