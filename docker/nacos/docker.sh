docker run \
  --name nacos-server \
  --restart always  \
  --publish 8848:8848 \
  --network nacos \
  --detach \
  --env MODE=standalone \
  nacos/nacos-server:1.2.1
