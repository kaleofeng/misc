docker run \
  --name tomcat_metazion_com_era \
  --network net_web \
  --restart always \
  -d \
  -p 8081:8080 \
  -v $PWD/conf/server.xml:/usr/local/tomcat/conf/server.xml \
  -v $PWD/webapps:/usr/local/tomcat/webapps \
  -v $PWD/logs:/usr/local/tomcat/logs \
  tomcat:9.0.35-jdk14-openjdk-oracle
