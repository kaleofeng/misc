FROM openjdk:15.0.1 AS base

LABEL maintainer="KaleoFeng" \
  version="1.0-SNAPSHOT" \
  description="Java application deployment purpose"

USER root

ENV TZ Asia/Shanghai
WORKDIR /data/bin
VOLUME [ "/data/bin" ]

COPY ./entrypoint.sh /
ENTRYPOINT [ "sh", "/entrypoint.sh" ]

EXPOSE 8080
CMD [ "java", "-jar", "./app.jar" ]
