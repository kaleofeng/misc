docker run \
  --name pycron \
  --restart=always \
  --volume $PWD/script:/data/script \
  --network docker_net_pycron \
  --detach \
  kaleofeng/pycron:1.0-SNAPSHOT
