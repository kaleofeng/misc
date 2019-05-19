docker run --name etcd_era --network net_ns -p 2379:2379 -p 2380:2380 --env ALLOW_NONE_AUTHENTICATION=yes -d --restart always bitnami/etcd:3.3.13
