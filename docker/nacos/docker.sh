docker run \
  --name nacos-server \
  --network nacos \
  --restart always  \
  --env MODE=standalone \
  -d \
  -p 8848:8848 \
  nacos/nacos-server:1.2.1
