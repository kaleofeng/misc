docker run --name mysql_era --network net_db -p 3306:3306 -v $PWD/conf:/etc/mysql -v $PWD/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=Root123456 -d --restart always mysql:8.0.13
