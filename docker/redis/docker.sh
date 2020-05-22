docker run \
  --name redis_era \
  --restart always \
  --publish 6379:6379 \
  --volume $PWD/conf:/etc/redis \
  --volume $PWD/data:/data \
  --network net_cache \
  --detach \
  redis:6.0.3 \
  redis-server /etc/redis/redis.conf
