docker run \
  --name tomcat_metazion_com_era \
  --restart always \
  --publish 8081:8080 \
  --volume $PWD/conf/server.xml:/usr/local/tomcat/conf/server.xml \
  --volume $PWD/webapps:/usr/local/tomcat/webapps \
  --volume $PWD/logs:/usr/local/tomcat/logs \
  --network net_web \
  --detach \
  tomcat:9.0.35-jdk14-openjdk-oracle
