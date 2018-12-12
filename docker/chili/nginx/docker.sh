docker run --name nginx_common -d -p 80:80 -v $PWD/conf/nginx.conf:/etc/nginx/nginx.conf -v $PWD/html:/var/share/nginx/html -v $PWD/logs:/var/log/nginx --link tomcat_metazion_com:tomcat_metazion_com --link tomcat_metazion_net:tomcat_metazion_net nginx:1.15.6