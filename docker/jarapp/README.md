# jarapp

Provides java jar app runtime environment

## Info

+ JDK `openjdk:15.0.1`
+ Time Zone `Asia/Shanghai`
+ Volume `/data/bin`
+ Service Port `8080`

## Usage

A typical jarapp directory view:

```shell
jarapp/
├── com
│   └── metazion
│       └── official
│           └── bin
│               └── official.jar
```

You can start an app with the following command:

```shell
docker run \
  --name jarapp_com_metazion_official_era \
  --restart=always \
  --publish 8080:8080 \
  --volume $PWD/com/metazion/official/bin:/data/bin \
  --detach \
  kaleofeng/jarapp:1.0-SNAPSHOT \
  java -Xms64m -Xmx64m -jar ./official.jar
```
