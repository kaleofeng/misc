docker run \
  --name rmqnamesrv_era \
  --restart always \
  --publish 9876:9876 \
  --volume $PWD/namesrv/store:/opt/store \
  --volume $PWD/namesrv/logs:/opt/logs \
  --network net_mq \
  --detach \
  --env "JAVA_OPTS=-Duser.home=/opt" \
  --env "JAVA_OPT_EXT=-server -Xms128m -Xmx128m -Xmn48m" \
  foxiswho/rocketmq:4.7.0 \
  sh mqnamesrv

docker run \
  --name rmqbroker_era \
  --restart always \
  --publish 10909:10909 \
  --publish 10911:10911 \
  --volume $PWD/broker/conf/broker.conf:/etc/rocketmq/broker.conf \
  --volume $PWD/broker/store:/opt/store \
  --volume $PWD/broker/logs:/opt/logs \
  --network net_mq \
  --detach \
  --env "JAVA_OPTS=-Duser.home=/opt" \
  --env "JAVA_OPT_EXT=-server -Xms128m -Xmx128m -Xmn48m" \
  foxiswho/rocketmq:4.7.0 \
  sh mqbroker -c /etc/rocketmq/broker.conf

docker run \
  --name rmqconsole_era \
  --restart always \
  --publish 9888:8080 \
  --network net_mq \
  --detach \
  --env "JAVA_OPTS=-Drocketmq.namesrv.addr=rmqnamesrv_era:9876 -Dcom.rocketmq.sendMessageWithVIPChannel=false" \
  styletang/rocketmq-console-ng:1.0.0
