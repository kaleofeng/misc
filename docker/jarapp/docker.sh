docker run \
  --name jarapp_official_era \
  --restart=always \
  --publish 8081:8080 \
  --volume $PWD/bin:/data/bin \
  --network net_web \
  --detach \
  kaleofeng/jarapp:1.0-SNAPSHOT \
  java -Xms64m -Xmx64m -jar ./official.jar
