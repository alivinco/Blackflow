FROM python:2.7.11-alpine
MAINTAINER Aleksandrs.Livincovs@gmail.com
RUN mkdir -p /var/lib/blackflow/apps/lib  \
    && mkdir -p /var/lib/blackflow/apps/data \
    && mkdir -p /var/log/blackflow/ \
    && touch /var/lib/blackflow/apps/__init__.py \
    && touch /var/lib/blackflow/apps/lib/__init__.py
RUN apk --no-cache add ca-certificates && update-ca-certificates
ADD ./blackflow /usr/lib/blackflow/blackflow
ADD ./blackflow/bin/blackflow_service.py /usr/lib/blackflow/
WORKDIR /usr/lib/blackflow
RUN ls -al /usr/lib/blackflow
#RUN rm -R /usr/lib/blackflow/blackflow/libs/site-packages/requests && rm -R /usr/lib/blackflow/blackflow/libs/site-packages/apscheduler
#RUN pip install six requests apscheduler
VOLUME ["/var/lib/blackflow/apps/"]
ENTRYPOINT python blackflow_service.py --apps /var/lib/blackflow/apps --log_dir /var/log/blackflow
