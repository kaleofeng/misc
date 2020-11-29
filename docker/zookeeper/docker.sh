docker run \
  --name zookeeper \
  --restart always  \
  --publish 2181:2181 \
  --volume /data/docker/zookeeper/conf/zoo.cfg:/conf/zoo.cfg \
  --network net_ns \
  --detach \
  zookeeper:3.6.1
