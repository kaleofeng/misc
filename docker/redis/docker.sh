docker run \
  --name redis_era \
  --network net_cache \
  --restart always \
  -d \
  -p 6379:6379 \
  -v $PWD/conf:/etc/redis \
  -v $PWD/data:/data \
  redis:5.0.5 \
  redis-server /etc/redis/redis.conf
