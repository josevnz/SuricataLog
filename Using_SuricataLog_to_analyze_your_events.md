# Using SuricataLog to analyze your events

This is condensed storyline from SuriCon 2024 (pre-SuriCon).

__Link to YouTube presentation will be shared soon!__

## Installing Suricata

```shell
sudo dnf install dnf-plugins-core
sudo dnf copr enable @oisf/suricata-7.0
sudo dnf install suricata
sudo vi /etc/sysconfig/suricata (setup network interfaces, etc)
sudo suricata-update && sudo suricata-update update-sources
for source in et/open osif/trafficid ptresearch/attackdetection tgreen/hunting malsilo/win-malware; do sudo suricata-update enable-source $source; done
sudo sudo suricata-update
sudo suricata-update list-enabled-sources
Sudo vi /etc/suricata/suricata.yaml # Bare minimum edit HOME_NET and make sure ‘payload: yes’
sudo systemctl enable suricata.service –now
sudo systemctl enable suricata-update.service –now
dnf -y install wireshark wireshark-cli # Yeah, it is super useful.
```

## Installing SuricataLogs

```shell
sudo python3 -m venv /usr/local/venvs/suricatalog && 
sudo -i # Yeah, let’s install this for all the users
. /usr/local/venvs/suricatalog/bin/activate
pip install –upgrade pip
pip install suricatalog # Watch the magic unfold!!!
eve_log --help
```

## Make Suricata works
### Use -l to save eve.json to a separate directory, for now
```shell
root@raspberypi1:/mnt/data/malware# sudo suricata -r /mnt/data/malware/2022-02-08-Emotet-epoch4-infection-start-and-spambot-traffic.pcap -k none --runmode autofp -c /etc/suricata/suricata.yaml -l /mnt/data/malware/
i: suricata: This is Suricata version 7.0.6 RELEASE running in USER mode
i: threads: Threads created -> RX: 1 W: 4 FM: 1 FR: 1   Engine started.
i: suricata: Signal Received.  Stopping engine.
i: pcap: read 1 file, 44949 packets, 32163467 bytes
```
### There is a lot of content
```shell
jq 'select(.event_type=="alert")' /mnt/data/malware/eve.json
```

## Running SuricataLog

```shell
eve_log /mnt/data/walmware/eve.json # eve.json as a nice table
eve_json --nxdomain /mnt/data/walmware/eve.json # DNS domains involved, queries
eve_json --useragent /mnt/data/walmware/eve.json # Any browser user agent?
eve_json --flow /mnt/data/walmware/eve-2.json # Packets by traffic
```

## Getting the source code
```shell
sudo dnf install -y git
git clone https://github.com/josevnz/SuricataLog
python3 -m venv ~/venv/suricatalog
. ~/venv/suricatalog/bin/activate
pip install –upgrade pip && pip install build
python3 -m build . # Get an wheelhouse
pip install --editable . # To really play
python3 -m unittest discover -s test -t test # Run unit tests
```

### Debugging a textualize application

On first terminal:

```shell
. ~/venv/suricatalog/bin/activate
pip install textual-dev==1.3.0
textual console
```

And on another:
```shell
. ~/venv/suricatalog/bin/activate
textual run --dev --command eve_json --payload test/eve.json
```