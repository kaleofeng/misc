# golapp

Provides golang app runtime environment

## Info

+ Golang `golang:1.18`
+ Time Zone `Asia/Shanghai`
+ Volume `/data/bin`
+ Service Port `8080`

## Usage

A typical golapp directory view:

```shell
golapp/
├── bin
│   ├── gotool
│   ├── log
│   │   └── gotool.log
│   └── resources
│       ├── static
│       │   ├── dictarticle
│       │   │   ├── input.js
│       │   │   └── output.js
│       │   └── image
│       │       └── favicon.ico
│       └── templates
│           ├── common_footer.html
│           ├── common_head.html
│           ├── dictarticle_input.html
│           └── dictarticle_output.html
```

You can start an app with the following command:

```shell
docker run \
  --name golapp_gotool_era \
  --restart=always \
  --publish 8080:8080 \
  --volume $PWD/bin:/data/bin \
  --detach \
  kaleofeng/golapp:1.0-SNAPSHOT \
  ./gotool
```
