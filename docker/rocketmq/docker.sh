docker run \
  --name rmqnamesrv_era \
  --network net_mq \
  --restart always \
  -d \
  -p 9876:9876 \
  -v $PWD/namesrv/store:/opt/store \
  -v $PWD/namesrv/logs:/opt/logs \
  -e "JAVA_OPTS=-Duser.home=/opt" \
  -e "JAVA_OPT_EXT=-server -Xms128m -Xmx128m -Xmn48m" \
  foxiswho/rocketmq:4.7.0 \
  sh mqnamesrv

docker run \
  --name rmqbroker_era \
  --network net_mq \
  --restart always \
  -d \
  -p 10909:10909 \
  -p 10911:10911 \
  -v $PWD/broker/conf/broker.conf:/etc/rocketmq/broker.conf \
  -v $PWD/broker/store:/opt/store \
  -v $PWD/broker/logs:/opt/logs \
  -e "JAVA_OPTS=-Duser.home=/opt" \
  -e "JAVA_OPT_EXT=-server -Xms128m -Xmx128m -Xmn48m" \
  foxiswho/rocketmq:4.7.0 \
  sh mqbroker -c /etc/rocketmq/broker.conf

docker run \
  --name rmqconsole_era \
  --network net_mq \
  --restart always \
  -d \
  -p 9888:8080 \
  -e "JAVA_OPTS=-Drocketmq.namesrv.addr=rmqnamesrv_era:9876 -Dcom.rocketmq.sendMessageWithVIPChannel=false" \
  styletang/rocketmq-console-ng:1.0.0
