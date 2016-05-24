FROM python:2.7.11-alpine
RUN mkdir -p /var/lib/blackflow/apps/lib  \
    && mkdir -p /var/lib/blackflow/apps/data \
    && mkdir -p /var/log/blackflow/ \
    && touch /var/lib/blackflow/apps/__init__.py \
    && touch /var/lib/blackflow/apps/lib/__init__.py
RUN apk --no-cache add ca-certificates && update-ca-certificates && ls -al /etc/ssl/certs
ADD ./blackflow /usr/lib/blackflow/blackflow
ADD ./blackflow/bin/blackflow_service.py /usr/lib/blackflow/
WORKDIR /usr/lib/blackflow
RUN ls -al /usr/lib/blackflow
RUN rm -R /usr/lib/blackflow/blackflow/libs/site-packages/requests && rm -R /usr/lib/blackflow/blackflow/libs/site-packages/apscheduler
#RUN pip install six requests apscheduler certifi
RUN pip install six requests apscheduler
ENV INSTANCE_NAME="default" MQTT_HOST="localhost" MQTT_PORT="1883"
ENTRYPOINT python blackflow_service.py --name $INSTANCE_NAME --apps /var/lib/blackflow/apps --log_dir /var/log/blackflow --mqtt_host $MQTT_HOST --mqtt_port $MQTT_PORT
