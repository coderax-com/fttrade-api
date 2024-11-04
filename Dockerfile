FROM python:3.12.7-bookworm
LABEL maintainer="Darwin M <darwin.molero@coderax.com>"

ENV PYTHONUNBUFFERED    1

RUN apt update \
    && apt install -y tree \
            cron \
            nano \
    && pip install --upgrade pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV EDITOR              nano

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

#
# Timezone
#
ENV TZ=Asia/Manila
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
