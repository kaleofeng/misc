docker run \
  --name frps \
  --network frp \
  -p 50000:50000 \
  -p 50500:50500 \
  -p 50080:50080 \
  -p 50443:50443 \
  -p 50022:50022 \
  -p 50122:50122 \
  -v /data/docker/frp/conf/frps.ini:/etc/frp/frps.ini  \
  -d \
  --restart=always  \
  snowdreamtech/frps
