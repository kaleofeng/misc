docker run \
  --name frps \
  --restart=always  \
  --publish 50000:50000 \
  --publish 50500:50500 \
  --publish 50080:50080 \
  --publish 50443:50443 \
  --publish 50022:50022 \
  --publish 50122:50122 \
  --volume $PWD/conf/frps.ini:/etc/frp/frps.ini \
  --network net_frp \
  --detach \
  snowdreamtech/frps:0.33.0
