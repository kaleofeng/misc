docker run \
  --name mysql_era \
  --network net_db \
  --restart always \
  -d \
  -p 3306:3306 \
  -v $PWD/conf:/etc/mysql \
  -v $PWD/data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=Root123456 \
  mysql:8.0.20 \
  --default-authentication-plugin=mysql_native_password
