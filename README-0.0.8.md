# SuricataLog

*NOTE: This README is for version 0.0.8. Please refer to default [README(README.md) for an up-to-date file.*

When I started learning how to use [Suricata](https://suricata.io/) quickly found that I needed a tool to inspect the eve.json file; Most of the tutorials 
and documentation out there suggested installing a stack to do the following tasks:
1. Store the logs in a central location
2. Normalize and enrich the events, specially alerts
3. Use a frontend to dive into the data

Which is very useful, but what if I just needed to do a quick inspection of the events?

Sooner or later you will get [bored to death](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html) doing this:

```shell
cat eve.json | jq -r -c 'select(.event_type=="alert")|.payload'| base64 --decode
```

SuricataLog is a set of tools/ scripts to parse and display Suricata log files (like /var/log/suricata/eve.json)

The [Eve JSON format](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-format.html) is not very complex, 
so I wrote few scripts with the features I tough would be more useful for my home network analysis.

As a bonus, I wrote my learning experience as a [tutorial](TUTORIAL.md) that you can use to learn about Suricata and also how to test it.

## Installing from PIP

Before you do anything else, make sure your environment is good to go:

```shell
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
```

### Installing from Pypi.org

```shell
pip3 install --upgrade SuricataLog
```

### Installing from source

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
python3 -m pip install --upgrade build
python3 -m build
pip3 install dist/SuricataLog-X.Y.Z-py3-none-any.whl
```

### Developer installation

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
pip install --upgrade pip
python -m pip install --upgrade build
python -m build
# python setup.py develop
pip install --editable .
```

Running unit tests is very easy after that:
```shell
python -m unittest test/test_suricatalog.py
...
----------------------------------------------------------------------
Ran 3 tests in 0.134s

OK

```

## Running the scripts

Once everything is installed you should be able to call the scripts

### Simple EVE log parser

Better see it by yourself

Table format:

[![asciicast](https://asciinema.org/a/494371.svg)](https://asciinema.org/a/494371)

````shell
eve_log.py --timestamp '2015-01-01 10:41:21.642899' --formats table test/eve.json
````

Show records in JSON format:

[![asciicast](https://asciinema.org/a/489775.svg)](https://asciinema.org/a/489775)

````shell
eve_log.py --timestamp '2015-01-01 10:41:21.642899' --formats json test/eve.json
````

Or brief format:

[![asciicast](https://asciinema.org/a/494375.svg)](https://asciinema.org/a/494375)

````shell
eve_log.py --timestamp '2015-01-01 10:41:21.642899' --formats brief test/eve.json
````

### Canned reports with eve_json.py

```shell
(suricatalog) [josevnz@dmaf5 SuricataLog]$ eve_json.py --help
usage: eve_json.py [-h] [--nxdomain | --payload | --flow | --netflow NETFLOW | --useragent] eve [eve ...]

This script is inspired by the examples provided on [15.1.3. Eve JSON ‘jq’ Examples](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-
examplesjq.html) A few things: * The output uses colorized JSON

positional arguments:
  eve                Path to one or more /var/log/suricata/eve.json file to parse.

optional arguments:
  -h, --help         show this help message and exit
  --nxdomain         Show DNS records with NXDOMAIN
  --payload          Show alerts with a printable payload
  --flow             Aggregated flow report per protocol and destination port
  --netflow NETFLOW  Get the netflow for a given IP address
  --useragent        Top user agent in HTTP traffic
```

#### NXDOMAIN

[![asciicast](https://asciinema.org/a/491442.svg)](https://asciinema.org/a/491442)

#### PAYLOAD

[![asciicast](https://asciinema.org/a/491432.svg)](https://asciinema.org/a/491432)

#### FLOW

[![asciicast](https://asciinema.org/a/491433.svg)](https://asciinema.org/a/491433)

#### NETFLOW

[![asciicast](https://asciinema.org/a/491435.svg)](https://asciinema.org/a/491435)

#### USERAGENT

[![asciicast](https://asciinema.org/a/491436.svg)](https://asciinema.org/a/491436)

## Running using a container

You only need to mount the eve.json file inside the container and call any of the scripts 
the same way you will on bare-metal.

### eve_log.json

You only need to mount the directory where the Suricata Eve files are saved

```shell
docker run --rm --interactive --tty --mount type=bind,source=/var/log/suricata/,destination=/logs,readonly suricatalog/eve_log:latest --timestamp '2022-02-23T18:22:24.405139+0000' --formats json /logs/eve.json
```

### eve_json.py
```shell
docker run --rm --interactive --tty --mount type=bind,source=/var/log/suricata/,destination=/logs,readonly suricatalog/eve_json:latest --nxdomain /logs/eve.json
```

### Building the Docker container

You need to build the images in order

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
BUILDKIT=1 docker build --tag suricatalog/eve_log --file Dockerfile .
BUILDKIT=1 docker build --tag suricatalog/eve_json --file Dockerfile-eve_json .
```

Why 2 Docker build files? I don't want to spawn any Shell processes inside the container, instead each container will be
very limited on what it can and cannot run.

## Supported versions

I work on this project on **my spare time** and I cannot support every version of Linux/ Python combination out there.
This is my current test bed, and it may change without further notice

| SuricataLog | Supported | OS                               | Python    | Suricata |
|-------------|-----------|----------------------------------|-----------|----------|
| <= 0.8      | NO        | NA                               | => 3.8    | 6.04     |
| 0.9         | YES       | fedora 37                        | => 3.11.4 | 6.04     |
| 0.9         | YES       | Armbian 23.02.2 Jammy            | => 3.10.6 | 6.04     |
| 0.9         | YES       | Ubuntu 20.04.4 LTS (Focal Fossa) | => 3.8.10 | 6.04     |

You are more than welcome to submit patches with new features and bug-fixes.


