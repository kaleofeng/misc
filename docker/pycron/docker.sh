docker run \
  --name pycron \
  --restart=always \
  --volume $PWD/script:/data/script \
  --network net_cron \
  --detach \
  kaleofeng/pycron:1.0-SNAPSHOT
