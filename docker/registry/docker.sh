docker run \
  --name registry \
  --restart always  \
  --publish 5000:5000 \
  --volume $PWD/registry:/var/lib/registry/ \
  --network registry \
  --detach \
  registry:2.7.1
