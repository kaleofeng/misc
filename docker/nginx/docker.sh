docker run \
  --name nginx_era \
  --restart always \
  --publish 80:80 \
  --publish 443:443 \
  --volume $PWD/conf/nginx.conf:/etc/nginx/nginx.conf \
  --volume $PWD/conf/cert:/etc/nginx/cert \
  --volume $PWD/html:/var/share/nginx/html \
  --volume $PWD/logs:/var/log/nginx \
  --network net_web \
  --detach \
  nginx:1.17.10
