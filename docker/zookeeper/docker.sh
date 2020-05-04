docker run \
  --name zookeeper \
  --network zookeeper \
  --restart=always  \
  -d \
  -p 2181:2181 \
  -v /data/docker/zookeeper/conf/zoo.cfg:/conf/zoo.cfg  \
  zookeeper
