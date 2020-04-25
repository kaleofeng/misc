docker run \
  --name etcd_era \
  --network net_ns \
  --restart always \
  --env ALLOW_NONE_AUTHENTICATION=yes \
  -d \
  -p 2379:2379 \
  -p 2380:2380 \
  bitnami/etcd:3.3.13
