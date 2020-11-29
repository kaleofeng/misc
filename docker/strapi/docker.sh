docker run \
  --name strapi_era \
  --restart=always \
  --publish 1337:1337 \
  --volume $PWD/app:/srv/app \
  --network net_web \
  --detach \
  --env DATABASE_CLIENT=mysql \
  --env DATABASE_NAME=strapi \
  --env DATABASE_HOST=datacenter.metazion.int \
  --env DATABASE_PORT=3306 \
  --env DATABASE_USERNAME=root \
  --env DATABASE_PASSWORD=Root123456 \
  strapi/strapi:3.1.6
