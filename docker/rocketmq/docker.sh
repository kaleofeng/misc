docker run \
  --name rmqserver_era \
  --network net_mq \
  --restart always \
  -d \
  -p 9876:9876 \
  -v $PWD/conf:/etc/rocketmq \
  -e "JAVA_OPTS=-Duser.home=/opt" \
  -e "JAVA_OPT_EXT=-server -Xms256m -Xmx256m -Xmn96m" \
  foxiswho/rocketmq:server-4.5.0

docker run \
  --name rmqbroker_era \
  --network net_mq \
  --restart always \
  -d \
  -p 10911:10911 \
  -p 10909:10909 \
  -v $PWD/conf:/etc/rocketmq \
  -e "JAVA_OPTS=-Duser.home=/opt" \
  -e "JAVA_OPT_EXT=-server -Xms256m -Xmx256m -Xmn96m" \
  foxiswho/rocketmq:broker-4.5.0

docker run \
  --name rmqconsole_era \
  --network net_mq \
  --restart always \
  -d \
  -p 9888:8080 \
  -e "JAVA_OPTS=-Drocketmq.namesrv.addr=rmqserver_era:9876 -Dcom.rocketmq.sendMessageWithVIPChannel=false" \
  styletang/rocketmq-console-ng:1.0.0
