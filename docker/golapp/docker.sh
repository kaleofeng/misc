docker run \
  --name golapp_gotool_era \
  --restart=always \
  --publish 8080:8080 \
  --volume $PWD/bin:/data/bin \
  --network net_web \
  --detach \
  kaleofeng/golapp:1.0-SNAPSHOT \
  ./gotool
