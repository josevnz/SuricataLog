# About SuricataLog

When I started learning how to use [Suricata](https://suricata.io/) quickly found that I needed a tool to inspect the eve.json file; Most of the tutorials 
and documentation out there suggested installing a stack to do the following tasks:
1. Store the logs in a central location
2. Normalize and enrich the events, specially alerts
3. Use a frontend to dive into the data

Which is very useful, but what if I just needed to do a quick inspection of the events?

Sooner or later you will get [bored to death](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html) doing this:

```shell
cat eve.json | jq -r -c 'select(.event_type=="alert")|.payload'|base64 --decode
```

SuricataLog is a set of tools/ scripts to parse and display Suricata log files (like /var/log/suricata/eve.json)

The [Eve JSON format](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-format.html) is not very complex, 
so I wrote few scripts with the features I tough would be more useful for my home network analysis.

As a bonus, I wrote my learning experience as a [tutorial](TUTORIAL.md) that you can use to learn about Suricata and also how to test it.

# Installing from PIP

Before you do anything else, make sure your environment is good to go:

```shell
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
python3 -m pip install --upgrade pip setuptools wheel
```

## Installing from Pypi.org

```shell
pip3 install --upgrade SuricataLog
```

## Installing from source

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
python3 -m pip install --upgrade build
python3 -m build
pip3 install dist/SuricataLog-X.Y.Z-py3-none-any.whl
```
## Developer installation

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
python3 -m venv ~/virtualenv/suricatalog
. ~/virtualenv/suricatalog/bin/activate
python3 setup.py develop
```

Running unit tests is very easy after that:
```shell
python -m unittest test/test_suricatalog.py
...
----------------------------------------------------------------------
Ran 3 tests in 0.134s

OK

```

# Running the scripts

Once everything is installed you should be able to call the scripts

## Simple even log parser

```shell
(suricatalog) [josevnz@dmaf5]$ eve_log.py --format table --timestamp '2022-02-23T19:00:00' test/eve.json 
Parsing test/eve.json ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
                                                    Suricata alerts for 2022-02-23 19:00:00, logs=test/eve.json                                                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Timestamp                       ┃ Severity ┃ Signature                                            ┃ Protocol ┃        Destination ┃             Source ┃ Payload ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 2022-02-23T19:07:02.373681+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49854 │   94.177.209.30:25 │         │
│ 2022-02-23T19:07:02.701847+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49855 │    210.131.2.36:25 │         │
│ 2022-02-23T19:07:03.423272+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49866 │   27.34.147.95:587 │         │
│ 2022-02-23T19:07:03.014386+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49859 │ 142.250.138.109:25 │         │
│ 2022-02-23T19:07:03.884078+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49865 │  122.17.147.238:25 │         │
│ 2022-02-23T19:07:01.976307+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49851 │    74.208.5.15:587 │         │
│ 2022-02-23T19:07:03.006849+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49857 │    74.208.5.15:587 │         │
│ 2022-02-23T19:07:02.508385+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49852 │ 116.254.112.253:25 │         │
│ 2022-02-23T19:07:03.018953+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49860 │  40.97.120.162:587 │         │
│ 2022-02-23T19:07:04.689953+0000 │ 3        │ SURICATA Applayer Detect protocol only one direction │     smtp │ 172.16.0.149:49862 │   192.185.4.31:587 │         │
└─────────────────────────────────┴──────────┴──────────────────────────────────────────────────────┴──────────┴────────────────────┴────────────────────┴─────────┘
```

Better see it by yourself, show eve log records in JSON format:

[![asciicast](https://asciinema.org/a/489775.svg)](https://asciinema.org/a/489775)

Or brief format:

[![asciicast](https://asciinema.org/a/489776.svg)](https://asciinema.org/a/489776)

Or in table format:

[![asciicast](https://asciinema.org/a/489777.svg)](https://asciinema.org/a/489777)

## Canned reports with eve_json.py

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

### NXDOMAIN

[![asciicast](https://asciinema.org/a/491442.svg)](https://asciinema.org/a/491442)

### PAYLOAD

[![asciicast](https://asciinema.org/a/491432.svg)](https://asciinema.org/a/491432)

### FLOW

[![asciicast](https://asciinema.org/a/491433.svg)](https://asciinema.org/a/491433)

### NETFLOW

[![asciicast](https://asciinema.org/a/491435.svg)](https://asciinema.org/a/491435)

### USERAGENT

[![asciicast](https://asciinema.org/a/491436.svg)](https://asciinema.org/a/491436)

# Running using a container

You only need to mount the eve.json file inside the container and call any of the scripts 
the same way you will on bare-metal.

## eve_log.json

You only need to mount the directory where the Suricata Eve files are saved

```shell
docker run --rm --interactive --tty --mount type=bind,source=/var/log/suricata/,destination=/logs,readonly suricatalog/eve_log:latest --timestamp '2022-02-23T18:22:24.405139+0000' --formats json /logs/eve.json
```

## eve_json.py
```shell
docker run --rm --interactive --tty --mount type=bind,source=/var/log/suricata/,destination=/logs,readonly suricatalog/eve_json:latest --nxdomain /logs/eve.json
```

## Building the Docker container

You need to build the images in order

```shell
git clone git@github.com:josevnz/SuricataLog.git
cd SuricataLog
BUILDKIT=1 docker build --tag suricatalog/eve_log --file Dockerfile-eve_log .
BUILDKIT=1 docker build --tag suricatalog/eve_json --file Dockerfile-eve_json .
```

Why 2 Docker build files? I don't want to spawn any Shell processes inside the container, instead each container will be
very limited on what it can and cannot run.
