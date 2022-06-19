# pycron

Provides crontab service with Python 3 on CentOS 8

## Info

+ System `Centos Stream 8`
+ Time Zone `Asia/Shanghai`
+ Volume `/data/script`
+ Python `python36 with openpyxl, pymysql and requests`

## Usage

A typical pycron directory view:

```shell
pycron/
└── script
    ├── conf
    │   └── db.conf
    ├── crontabs
    └── worldometers
        ├── data
        │   └── country_gdp_2022-06-19-09-48-00.xlsx
        ├── gdp.py
        └── log
            └── gdp.log
```

File `crontabs` content:

```shell
59 23 * * * flock -xn /tmp/worldometers_gdp.lock -c 'timeout 5m /usr/bin/python3 /data/script/worldometers/gdp.py >> /data/script/worldometers/log/gdp.log 2>&1'
```

You can start a crontab with the following command:

```shell
docker run \
  --name pycron \
  --restart=always \
  --volume $PWD/script:/data/script \
  --detach \
  kaleofeng/pycron:1.0-SNAPSHOT
```
