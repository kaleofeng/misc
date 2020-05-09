docker run \
  --name nacos-server \
  --network nacos \
  --restart always  \
  --env MODE=standalone \
  -d \
  -p 8848:8848 \
  -v $PWD/conf:/home/nacos/conf/  \
  nacos/nacos-server
