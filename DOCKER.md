# Docker build

Here you will find instructions on how to build a custom Docker container for SuricataLog.

It is assumed you have docker-ce version '24.0.7' or better.

## Create the wheelhouse 

You need to have the SuricataLog wheelhouse

```shell
test -d dist && rm -f dist/*
python -m venv ~/virtualenv/SuricataLog
. ~/virtualenv/SuricataLog/bin/activate
pip install --upgrade pip
pip install build
pip install wheel
python -m build .
```

## Create the Docker image

```shell
docker compose build
docker images suricatalog:latest
```

If the image was built correctly, you will see something like this:

```shell
(SuricataLog) [josevnz@dmaf5 SuriCon-2024]$ docker images suricatalog:latest
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
suricatalog   latest    ed1aaac1f3de   6 minutes ago   173MB
```


