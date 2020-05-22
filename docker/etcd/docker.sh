docker run \
  --name etcd_era \
  --restart always \
  --publish 2379:2379 \
  --publish 2380:2380 \
  --network net_ns \
  --detach \
  --env ALLOW_NONE_AUTHENTICATION=yes \
  --env ETCD_ADVERTISE_CLIENT_URLS=http://etcd:2379 \
  bitnami/etcd:3.4.9
