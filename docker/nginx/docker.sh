docker run \
  --name nginx_era \
  --network net_web \
  --restart always \
  -d \
  -p 80:80 \
  -p 443:443 \
  -v $PWD/conf/nginx.conf:/etc/nginx/nginx.conf \
  -v $PWD/conf/cert:/etc/nginx/cert \
  -v $PWD/html:/var/share/nginx/html \
  -v $PWD/logs:/var/log/nginx \
  nginx:1.15.6
