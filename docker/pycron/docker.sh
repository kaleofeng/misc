docker run \
  --name pycron \
  --network pycron \
  --restart=always \
  -d \
  -v $PWD/script:/data/script \
  kaleofeng/pycron:0.0.1
