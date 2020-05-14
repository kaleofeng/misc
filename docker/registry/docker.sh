docker run \
  --name registry \
  --network registry \
  --restart always  \
  -d \
  -p 5000:5000 \
  -v $PWD/registry:/var/lib/registry/ \
  registry
