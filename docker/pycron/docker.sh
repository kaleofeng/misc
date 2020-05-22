docker run \
  --name pycron \
  --restart=always \
  --volume $PWD/script:/data/script \
  --network net_pycron \
  --detach \
  kaleofeng/pycron:0.0.1
