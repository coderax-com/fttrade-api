FROM python:3.12.7-bookworm
LABEL maintainer="Darwin M <darwin.molero@coderax.com>"

ENV PYTHONUNBUFFERED    1

RUN apt update \
    && apt install -y --no-install-recommends \
            tree \
            cron \
            nano \
    && pip install --upgrade pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV EDITOR              nano

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

#
# cron
#
COPY cron/fttrade_cron /etc/cron.d/
RUN chmod 0644 /etc/cron.d/fttrade_cron
RUN crontab /etc/cron.d/fttrade_cron
COPY cron/cron_script.sh /var/opt/cron_script.sh
RUN chmod 0744 /var/opt/cron_script.sh
RUN touch /var/log/cron.log

#
# Timezone
#
ENV TZ=Asia/Manila
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

#
# entrypoint
#
COPY entrypoint.sh /var/opt/entrypoint.sh
RUN chmod +x /var/opt/entrypoint.sh
ENTRYPOINT ["/var/opt/entrypoint.sh"]
