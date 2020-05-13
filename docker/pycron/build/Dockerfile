FROM centos:8

LABEL maintainer="KaleoFeng" \
  version="0.0.1-SNAPSHOT" \
  description="Crontab with Python 3 on CentOS 8"

USER root

RUN \cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

RUN dnf -y module install python36; \
  pip3 install pymysql; \
  pip3 install xlwt; \
  pip3 install requests; \
  dnf -y install cronie crontabs

VOLUME [ "/data/script" ]

COPY ./entrypoint.sh .
ENTRYPOINT [ "sh", "./entrypoint.sh" ]

CMD [ "/usr/sbin/crond", "-n" ]
