docker run --name redis_era --network net_cache -p 6379:6379 -v $PWD/conf:/etc/redis -v $PWD/data:/data -d --restart always redis:5.0.5 redis-server /etc/redis/redis.conf
