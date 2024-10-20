# Docker

## Building the image using the cloned repository

Here you will find instructions on how to build a custom Docker container for SuricataLog.

It is assumed you have docker-ce version '24.0.7' or better.

### Create the wheelhouse 

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

### Create the Docker image

```shell
docker compose --file docker-compose.yml build
docker images suricatalog:latest
```

If the image was built correctly, you will see something like this:

```shell
(SuricataLog) [josevnz@dmaf5 SuriCon-2024]$ docker images suricatalog:latest
REPOSITORY    TAG       IMAGE ID       CREATED         SIZE
suricatalog   latest    ed1aaac1f3de   6 minutes ago   173MB
```

## Running the container

You first start a docker container, and then you can attach to it. You need to pass the directory where you have your
eve.json files so the volume is accessible to SuricataLog

### Using docker compose

If you download the [docker-compose.yml](docker-compose.yml) you can then do the following, with less typing:


```shell
docker compose --file docker-compose.yml up --detach
```

And then you can either log into the container and run commands from there:

```shell
docker compose exec suricatalog /bin/bash -l
# to explore (press eve_ + <TAB> to autocomplete):
eve_log eve.json
eve_json --flow eve.json
```

Or run commands from outside the container:

```shell
docker compose exec suricatalog eve_log eve.json
docker compose exec suricatalog eve_json --flow eve.json
```

To stop the container:

```shell
docker compose stop suricatalog
```

#### Too much typing? Set up a function

```shell
function sl { docker compose exec suricatalog $*; }
sl eve_log eve.json
sl eve_json --flow eve.json
```

You get the idea.

### Using docker command

If you prefer to have more control you can run the container directly

```shell
docker run --restart always --detach --tty --volume $PWD/test:/suricatalog --name suricatalog suricatalog:latest

# Run eve_log
docker exec --interactive --tty suricatalog eve_log /suricatalog/eve.json

# Exit and then run eve_json
docker exec --interactive --tty suricatalog eve_json --payload /suricatalog/eve.json
```

Once you are done with the container you can kill it with:

```shell
docker stop suricatalog
```

