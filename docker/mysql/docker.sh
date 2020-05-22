docker run \
  --name mysql_era \
  --restart always \
  --publish 3306:3306 \
  --volume $PWD/conf:/etc/mysql \
  --volume $PWD/data:/var/lib/mysql \
  --network net_db \
  --detach \
  --env MYSQL_ROOT_PASSWORD=Root123456 \
  mysql:8.0.20 \
  --default-authentication-plugin=mysql_native_password
