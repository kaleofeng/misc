FROM openjdk:15

LABEL maintainer="KaleoFeng" \
  version="1.0-SNAPSHOT" \
  description="Provides java app runtime environment"

USER root

ENV TZ Asia/Shanghai

WORKDIR /data/bin
VOLUME [ "/data/bin" ]

COPY ./entrypoint.sh /
ENTRYPOINT [ "bash", "/entrypoint.sh" ]

EXPOSE 8080
CMD [ "java", "-jar", "./app.jar" ]
