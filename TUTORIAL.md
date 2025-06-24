# Suricata, RaspberryPI4 and Python to secure your home network

(Original article published on freecodecamp.org: [Home Network Security – How to Use Suricata, RaspberryPI4, and Python to Make Your Network Safe](https://www.freecodecamp.org/news/home-network-security-with-suricata-raspberrypi4-python/))

In a [previous article](https://www.freecodecamp.org/news/wireless-security-using-raspberry-pi-4-kismet-and-python/) I showed you how to secure your wireless home network using [Kismet](https://www.kismetwireless.net/).

Kismet is perfect on detecting anomalies and certain types of attack, but what if I want to analyze the traffic and look for abnormal patterns or patterns that could indicate an attack?

And [Intrusion Detection System](https://en.wikipedia.org/wiki/Intrusion_detection_system) (**IDS**) is:

> An intrusion detection system (IDS; also intrusion prevention system or IPS) is a device or software application that monitors a network or systems for malicious activity or policy violations

I used a good IDS in the past called [Snort V2](https://snort.org/), I'm awarer than *Snort 3 is out* but there is a [pretty clear warning](https://snort.org/documents/snort-supported-oss) about running it on a machine without much memory:

> While Snort can compile on almost all *nix based machines, it is not recommended that you compile Snort on a low power or low RAM machine. Snort requires memory to run and to properly analyze as much traffic as possible.

And

> Snort does not officially support any particular OS

_Not exactly a reason to dislike it_, but I feel more confident when a vendor tells me than my OS is in their supported platform list; I do also have more recent experience setting up with [Suricata,](https://suricata.io/download/) so I decided to give it a more serious try to keep tabs on my local network and alert me if any suspicious activity is detected. Poking around I found than for my local network, 8 GB of RAM will be sufficient and my Linux distribution

```shell=
josevnz@raspberrypi:~$ lsb_release --release
Release:	20.04
```

My version of Ubuntu _is supported out of the box_.

The choice is yours, *In my case* it felt better to use Suricata than Snort; as usual you need to plan around your hardware, your use cases and features offered by the tools (including commercial support).

# Quick installation

Installation is explained in detail [here](https://redmine.openinfosecfoundation.org/projects/suricata/wiki/Ubuntu_Installation_-_Personal_Package_Archives_%28PPA%29), so I will only put here the [quick installation steps](https://www.youtube.com/playlist?list=PLFqw30a25lWRIhAnQNb7ZaPpexPYgxhVv) I used on my machine:

```shell=
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt-get update
sudo apt-get install suricata 
```

## Suricata is a complex beast, will stick to the IDS mode on this tutorial/

You can use Suricata to *detect and alert about anomalies* in your network traffic (IDS) or you can proactively drop suspicious connections when working in _Intrusion Prevention System (**IPS**)_. It can also capture network traffic
and store it in PCAP format for later analysis (be careful as you can eat your disk space pretty fast).

We will keep things simple, for now will take a more passive approach and get alerts when an intrusion is detected

# Where you should connect your RaspBerryPI 4 with Suricata?

Ideally you want to put your Suricata sensor close to your home router; One way to do it is to connect all the devices (including your home router) to a common switch, and
then mirror the traffic that goes in/ out the home router into a port on the switch. Suricata will be connected to that port, listening to all the traffic.

If you wanted to run Suricata as an IPS then the connectivity would have to be different, but this is not the intended use on this tutorial.

# Setting up Suricata

Ideally the best placement to put Suricata is between a firewall and the rest of servers in your home network; In this scenario let's assume than it is not possible because there is no firewall (OK, that will be your ISP router, but you cannot run Suricata there), so the next best thing is the wired network interface connected to it (in my case eth0)

The /etc/suricata/suricata.yaml file contains the defaults. I'll show here what I overrode:

```shell
root@raspberrypi:~# grep -in1 af-p /etc/suricata/suricata.yaml 
580-# Linux high speed capture support
581:af-packet:
582-  - interface: eth0
root@raspberrypi:~# grep -in 'HOME_NET: "' /etc/suricata/suricata.yaml |grep -v '#'
15:    HOME_NET: "[192.168.1.0/24]"
```

Start Suricata:
```shell
root@raspberrypi:~# systemctl start suricata.service
root@raspberrypi:~# systemctl status suricata.service
● suricata.service - LSB: Next Generation IDS/IPS
     Loaded: loaded (/etc/init.d/suricata; generated)
     Active: active (running) since Sun 2022-04-10 23:49:00 UTC; 24h ago
       Docs: man:systemd-sysv-generator(8)
      Tasks: 10 (limit: 9257)
     CGroup: /system.slice/suricata.service
             └─1834983 /usr/bin/suricata -c /etc/suricata/suricata.yaml --pidfile /var/run/suricata.pid --af-packet -D -vvv

Apr 10 23:49:00 raspberrypi systemd[1]: Starting LSB: Next Generation IDS/IPS...
Apr 10 23:49:00 raspberrypi suricata[1834973]: Starting suricata in IDS (af-packet) mode... done.
Apr 10 23:49:00 raspberrypi systemd[1]: Started LSB: Next Generation IDS/IPS.
```

The important details go into the file '/var/log/suricata/eve.json'. Mine started to grow surprisingly fast after starting Suricata:

```json lines
{"timestamp":"2022-04-10T23:49:32.527488+0000","event_type":"stats","stats":{"uptime":32,"capture":{"kernel_packets":113,"kernel_drops":0,"errors":0},"decoder":{"pkts":126,"bytes":17986,"invalid":0,"ipv4":30,"ipv6":74,"ethernet":126,"chdlc":0,"raw":0,"null":0,"sll":0,"tcp":4,"udp":30,"sctp":0,"icmpv4":0,"icmpv6":70,"ppp":0,"pppoe":0,"geneve":0,"gre":0,"vlan":0,"vlan_qinq":0,"vxlan":0,"vntag":0,"ieee8021ah":0,"teredo":0,"ipv4_in_ipv6":0,"ipv6_in_ipv6":0,"mpls":0,"avg_pkt_size":142,"max_pkt_size":392,"max_mac_addrs_src":0,"max_mac_addrs_dst":0,"erspan":0,"event":{"ipv4":{"pkt_too_small":0,"hlen_too_small":0,"iplen_smaller_than_hlen":0,"trunc_pkt":0,"opt_invalid":0,"opt_invalid_len":0,"opt_malformed":0,"opt_pad_required":0,"opt_eol_required":0,"opt_duplicate":0,"opt_unknown":0,"wrong_ip_version":0,"icmpv6":0,"frag_pkt_too_large":0,"frag_overlap":0,"frag_ignored":0},"icmpv4":{"pkt_too_small":0,"unknown_type":0,"unknown_code":0,"ipv4_trunc_pkt":0,"ipv4_unknown_ver":0},"icmpv6":{"unknown_type":0,"unknown_code":0,"pkt_too_small":0,"ipv6_unknown_version":0,"ipv6_trunc_pkt":0,"mld_message_with_invalid_hl":0,"unassigned_type":0,"experimentation_type":0},"ipv6":{"pkt_too_small":0,"trunc_pkt":0,"trunc_exthdr":0,"exthdr_dupl_fh":0,"exthdr_useless_fh":0,"exthdr_dupl_rh":0,"exthdr_dupl_hh":0,"exthdr_dupl_dh":0,"exthdr_dupl_ah":0,"exthdr_dupl_eh":0,"exthdr_invalid_optlen":0,"wrong_ip_version":0,"exthdr_ah_res_not_null":0,"hopopts_unknown_opt":0,"hopopts_only_padding":0,"dstopts_unknown_opt":0,"dstopts_only_padding":0,"rh_type_0":0,"zero_len_padn":21,"fh_non_zero_reserved_field":0,"data_after_none_header":0,"unknown_next_header":0,"icmpv4":0,"frag_pkt_too_large":0,"frag_overlap":0,"frag_invalid_length":0,"frag_ignored":0,"ipv4_in_ipv6_too_small":0,"ipv4_in_ipv6_wrong_version":0,"ipv6_in_ipv6_too_small":0,"ipv6_in_ipv6_wrong_version":0},"tcp":{"pkt_too_small":0,"hlen_too_small":0,"invalid_optlen":0,"opt_invalid_len":0,"opt_duplicate":0},"udp":{"pkt_too_small":0,"hlen_too_small":0,"hlen_invalid":0},"sll":{"pkt_too_small":0},"ethernet":{"pkt_too_small":0},"ppp":{"pkt_too_small":0,"vju_pkt_too_small":0,"ip4_pkt_too_small":0,"ip6_pkt_too_small":0,"wrong_type":0,"unsup_proto":0},"pppoe":{"pkt_too_small":0,"wrong_code":0,"malformed_tags":0},"gre":{"pkt_too_small":0,"wrong_version":0,"version0_recur":0,"version0_flags":0,"version0_hdr_too_big":0,"version0_malformed_sre_hdr":0,"version1_chksum":0,"version1_route":0,"version1_ssr":0,"version1_recur":0,"version1_flags":0,"version1_no_key":0,"version1_wrong_protocol":0,"version1_malformed_sre_hdr":0,"version1_hdr_too_big":0},"vlan":{"header_too_small":0,"unknown_type":0,"too_many_layers":0},"ieee8021ah":{"header_too_small":0},"vntag":{"header_too_small":0,"unknown_type":0},"ipraw":{"invalid_ip_version":0},"ltnull":{"pkt_too_small":0,"unsupported_type":0},"sctp":{"pkt_too_small":0},"mpls":{"header_too_small":0,"pkt_too_small":0,"bad_label_router_alert":0,"bad_label_implicit_null":0,"bad_label_reserved":0,"unknown_payload_type":0},"vxlan":{"unknown_payload_type":0},"geneve":{"unknown_payload_type":0},"erspan":{"header_too_small":0,"unsupported_version":0,"too_many_vlan_layers":0},"dce":{"pkt_too_small":0},"chdlc":{"pkt_too_small":0}},"too_many_layers":0},"flow":{"memcap":0,"tcp":1,"udp":20,"icmpv4":0,"icmpv6":15,"tcp_reuse":0,"get_used":0,"get_used_eval":0,"get_used_eval_reject":0,"get_used_eval_busy":0,"get_used_failed":0,"wrk":{"spare_sync_avg":100,"spare_sync":4,"spare_sync_incomplete":0,"spare_sync_empty":0,"flows_evicted_needs_work":0,"flows_evicted_pkt_inject":0,"flows_evicted":0,"flows_injected":0},"mgr":{"full_hash_pass":1,"closed_pruned":0,"new_pruned":0,"est_pruned":0,"bypassed_pruned":0,"rows_maxlen":1,"flows_checked":4,"flows_notimeout":4,"flows_timeout":0,"flows_timeout_inuse":0,"flows_evicted":0,"flows_evicted_needs_work":0},"spare":9600,"emerg_mode_entered":0,"emerg_mode_over":0,"memuse":11668608},"defrag":{"ipv4":{"fragments":0,"reassembled":0,"timeouts":0},"ipv6":{"fragments":0,"reassembled":0,"timeouts":0},"max_frag_hits":0},"flow_bypassed":{"local_pkts":0,"local_bytes":0,"local_capture_pkts":0,"local_capture_bytes":0,"closed":0,"pkts":0,"bytes":0},"tcp":{"sessions":0,"ssn_memcap_drop":0,"pseudo":0,"pseudo_failed":0,"invalid_checksum":0,"no_flow":0,"syn":0,"synack":0,"rst":0,"midstream_pickups":0,"pkt_on_wrong_thread":0,"segment_memcap_drop":0,"stream_depth_reached":0,"reassembly_gap":0,"overlap":0,"overlap_diff_data":0,"insert_data_normal_fail":0,"insert_data_overlap_fail":0,"insert_list_fail":0,"memuse":2424832,"reassembly_memuse":393216},"detect":{"engines":[{"id":0,"last_reload":"2022-04-10T23:49:00.377030+0000","rules_loaded":0,"rules_failed":0}],"alert":0},"app_layer":{"flow":{"http":0,"ftp":0,"smtp":0,"tls":0,"ssh":0,"imap":0,"smb":0,"dcerpc_tcp":0,"dns_tcp":0,"nfs_tcp":0,"ntp":1,"ftp-data":0,"tftp":0,"ikev2":0,"krb5_tcp":0,"dhcp":0,"snmp":0,"sip":0,"rfb":0,"mqtt":0,"rdp":0,"failed_tcp":0,"dcerpc_udp":0,"dns_udp":0,"nfs_udp":0,"krb5_udp":0,"failed_udp":19},"tx":{"http":0,"ftp":0,"smtp":0,"tls":0,"ssh":0,"imap":0,"smb":0,"dcerpc_tcp":0,"dns_tcp":0,"nfs_tcp":0,"ntp":1,"ftp-data":0,"tftp":0,"ikev2":0,"krb5_tcp":0,"dhcp":0,"snmp":0,"sip":0,"rfb":0,"mqtt":0,"rdp":0,"dcerpc_udp":0,"dns_udp":0,"nfs_udp":0,"krb5_udp":0},"expectations":0},"http":{"memuse":0,"memcap":0},"ftp":{"memuse":0,"memcap":0},"file_store":{"open_files":0}}}
```

_Holy Priceless Collection of Etruscan Snoods!, Batman_; how do we tune Suricata to avoid this overwhelming amount of information?

For now let's stop it while we figure it out.

# Tuning up Suricata

## Make sure settings of suricata.yaml made sense for a home network

```shell
sudo -i
# And a YAML linter so we can make sure our Suricata configuration files are good
apt-get install yamllint
cp -v -p  /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.orig
```

*Note:* I provide here a linted and clean version of my [suricata.yaml](etc/suricata/suricata.yaml) file.

## Tame the /var/log/suricata/eve.json

That is the file were we can learn in detail what triggered an alert. But It can grow up VERY fast, depending on your traffic and event rules configuration.

So using logrotate (comes installed as part of Ubuntu):

```
# Keep a week of logs, 1 GB of size.
# Always test your config: logrotate -vdf /etc/logrotate.d/suricata
/var/log/suricata/*.log /var/log/suricata/*.json {
    daily
    maxsize 1G
    rotate 7
    missingok
    nocompress
    create
    sharedscripts
    postrotate
        systemctl restart suricata.service
    endscript
}
```

## Helping Suricata to do its job using Emerging threats rules

We can tune Suricata using the [ET OPEN Ruleset](https://rules.emergingthreats.net/OPEN_download_instructions.html); Because threats change all the time, 
you need to automate [their download and updating](https://github.com/OISF/suricata-update#suricata-update).

So install it first:

```shell
sudo -i
python3 -m venv ~/virtualenv/suricata
. ~/virtualenv/suricata/bin/activate
pip install --upgrade pip
pip install --upgrade suricata-update
suricata-update
# Also, install jq so we can see the contents of the eve.json file nicely formatted
apt-get install jq
```

Let's run it by hand and see how the rules are updated by the tool:

[![asciicast](https://asciinema.org/a/487861.svg)](https://asciinema.org/a/487861)

For our home network, we will download these rules once a day, 
a [simple Cron job](https://en.wikipedia.org/wiki/Cron) will do the trick ():

```shell
crontab -e
# Run Suricata update once a day, 
# per https://rules.emergingthreats.net/OPEN_download_instructions.html
# Also will update at a different time than the log rotation, to avoid a race condition
# while rotating the logs. Note than we do not need to restart suricata
0 30 * * * . ~/virtualenv/suricata/bin/activate && suricata-update && suricatasc -c reload-rules
```

Let's start suricata again, so we can test some rules:

[![asciicast](https://asciinema.org/a/487868.svg)](https://asciinema.org/a/487868)

## What is inside the /var/log/suricata/eve.json file?

The file packs quite a bit of information, which is [described in detail](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-format.html) here:

```json lines
{"timestamp":"2022-04-15T20:52:05.026189+0000","flow_id":1378250082748552,"in_iface":"eth0","event_type":"flow","src_ip":"192.168.1.1","src_port":59317,"dest_ip":"239.255.255.250","dest_port":1900,"proto":"UDP","app_proto":"failed","flow":{"pkts_toserver":1,"pkts_toclient":0,"bytes_toserver":378,"bytes_toclient":0,"start":"2022-04-15T20:50:32.264328+0000","end":"2022-04-15T20:50:32.264328+0000","age":0,"state":"new","reason":"timeout","alerted":false}}
{"timestamp":"2022-04-15T20:52:05.026418+0000","flow_id":2222739437411106,"in_iface":"eth0","event_type":"flow","src_ip":"192.168.1.1","src_port":60890,"dest_ip":"239.255.255.250","dest_port":1900,"proto":"UDP","app_proto":"failed","flow":{"pkts_toserver":1,"pkts_toclient":0,"bytes_toserver":376,"bytes_toclient":0,"start":"2022-04-15T20:50:32.482082+0000","end":"2022-04-15T20:50:32.482082+0000","age":0,"state":"new","reason":"timeout","alerted":false}}
```

If you are casually inspecting the contents of the file in real time, I suggest you use [jq](https://stedolan.github.io/jq/) (test your filters on [jqplay.org](https://jqplay.org/)) and show a few fields of interest:

[![asciicast](https://asciinema.org/a/487979.svg)](https://asciinema.org/a/487979)

*Note*: Going forward we will focus on the alerts, so we can just filter out by that type of event:

```shell
jq 'select(.event_type=="alert")' /var/log/suricata/eve.json
```

The Suricata folks have [put a nice page with examples](https://suricata.readthedocs.io/en/suricata-6.0.0/output/eve/eve-json-examplesjq.html) that you should check out.

## Testing Suricata installation

### Tools of the trade: Wireshark, tcpreplay and PCAP files

We will use some traffic capture files, in [PCAP](https://tools.ietf.org/id/draft-gharris-opsawg-pcap-00.html) format.
So what is a PCAP file?

> In the late 1980's, Van Jacobson, Steve McCanne, and others at the Network Research Group at Lawrence Berkeley National Laboratory developed the [tcpdump](https://www.tcpdump.org/) 
> program to capture and dissect network traces. The code to capture traffic, using low-level mechanisms in various operating systems, and to read and write network traces 
> to a file was later put into a library named libpcap

And we will use a tool to inspect the contents of the PCAP file; [Wireshark](https://www.wireshark.org/) is a powerful traffic analysis tool, and we will use [tcpreplay](https://tcpreplay.appneta.com/) to trigger the Suricata alerts by playing a PCAP file with suspicious activity:

```shell
# On Ubuntu, Debian: sudo apt-get install wireshark tcpreplay
sudo dnf install -y wireshark tcpreplay
```

The best way to learn how the bad actors operate is to see their footprints!. You should definitely head to [https://www.malware-traffic-analysis.net/](https://www.malware-traffic-analysis.net/) and download some samples, 
an even [better practice](https://www.malware-traffic-analysis.net/training-exercises.html) with their PCAP analysis exercises.

### **WARNING**: You will be downloading files that are dangerous:

> Use this website at your own risk!  If you download or use of any information from this website, you assume complete responsibility for any resulting loss or damage.

So be careful and responsible when using this network traffic captures.

#### No rules are enabled by default?

How we can check if that is the case? I'll show you next:

[![asciicast](https://asciinema.org/a/488000.svg)](https://asciinema.org/a/488000)

Once you enable the rules ``(suricata-update list-sources --free; uricata-update enable-source source; suricata-update list-enabled-sources)`` you can tell Suricata to reload the rules without a reboot:

```shell
root@raspberrypi:~# suricatasc -c reload-rules
{"message": "done", "return": "OK"}
```

### 2022-02-23 - TRAFFIC ANALYSIS EXERCISE - SUNNYSTATION

Let's see if we can trigger Suricata using this specific threat (it is relative new).

Start by downloading [2022-02-23-traffic-analysis-exercise.pcap.zip](https://www.malware-traffic-analysis.net/2022/02/23/2022-02-23-traffic-analysis-exercise.pcap.zip), the password is on the [about page]().

```shell
insta_dir="$HOME/Downloads/malware/"
mkdir --parent --verbose "$insta_dir"
url="https://www.malware-traffic-analysis.net/2022/02/23/2022-02-23-traffic-analysis-exercise.pcap.zip"
exercise=$(basename $url)
curl --fail --location --output "$insta_dir/$exercise" $url
# Be ready to put the password :-)
cd $insta_dir && unzip $exercise 
```

What is inside? we can check with _capinfos_ to get some insight on the file we just downloaded:

```shell  
[josevnz@dmaf5 malware]$ capinfos 2022-02-23-traffic-analysis-exercise.pcap
File name:           2022-02-23-traffic-analysis-exercise.pcap
File type:           Wireshark/tcpdump/... - pcap
File encapsulation:  Ethernet
File timestamp precision:  microseconds (6)
Packet size limit:   file hdr: 65535 bytes
Number of packets:   30k
File size:           19MB
Data size:           19MB
Capture duration:    2680.736661 seconds
First packet time:   2022-02-23 13:22:24.405139
Last packet time:    2022-02-23 14:07:05.141800
Data byte rate:      7,191 bytes/s
Data bit rate:       57kbps
Average packet size: 642.09 bytes
Average packet rate: 11 packets/s
SHA256:              eefc7e61b50e7846f5a3282d7645539d7b2b4b85aa08a09d0b823896c9449d1f
RIPEMD160:           a8d84d262e37563c179e9ca52cdc6aae271efd9c
SHA1:                fdfa0d0edfe0cbcc0c1400fbe6ac61ff40942755
Strict time order:   True
Number of interfaces in file: 1
Interface #0 info:
                     Encapsulation = Ethernet (1 - ether)
                     Capture length = 65535
                     Time precision = microseconds (6)
                     Time ticks per second = 1000000
                     Number of stat entries = 0
                     Number of packets = 30023
```

Will use a [small wrapper](scripts/replay_pcap_file.sh) around _tcpreplay_ to replay our PCAP file:

```shell
#!/bin/bash
:<<DOC
Script to replay a PCAP file at accelerated pace on the default network interface
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
DOC
default_dev=$(ip route show| grep default| sort -n -k 9| head -n 1| cut -f5 -d' ')|| exit 100
if [ "$(id --name --user)" != "root" ]; then
  echo "ERROR: I need to be root to inject the PCAP contents into '$default_dev'"
  echo "Maybe 'sudo $0 $*'?"
  exit 100
fi
for util in tcpreplay ip; do
  if ! type -p $util > /dev/null 2>&1; then
    echo "Please put $util on the PATH and try again!"
    exit 100
  fi
done
:<<DOC
We may have more than one 'default' route, so we sort by priority and pick the one with the
preferred metric:
default via 192.168.1.1 dev eno1 proto dhcp metric 100 <----- PICK ME!!!
default via 192.168.1.1 dev wlp4s0 proto dhcp metric 600
DOC
for pcap in "$@"; do
  if [ -f "$pcap" ]; then
    if ! tcpreplay --stats 5 --intf1 "$default_dev" --multiplier 24 "$pcap"; then
      echo "ERROR: Will not try to replay any pending PCAP files due previous errors"
      exit 100
    fi
  fi
done
```

Let it replay until it reaches the end of the file:

```shell
root@raspberrypi:~# tcpreplay --stats 5 --intf1 eth0 --multiplier 24 ~josevnz/Downloads/malware/2022-02-23-traffic-analysis-exercise.pcap 
Test start: 2022-04-16 17:51:40.673394 ...
Actual: 3783 packets (1075843 bytes) sent in 5.03 seconds
Rated: 213624.5 Bps, 1.70 Mbps, 751.17 pps
Actual: 6959 packets (3325918 bytes) sent in 10.04 seconds
Rated: 331191.4 Bps, 2.64 Mbps, 692.96 pps
Actual: 8627 packets (4464002 bytes) sent in 15.14 seconds
Rated: 294744.2 Bps, 2.35 Mbps, 569.61 pps
Actual: 10975 packets (6331901 bytes) sent in 20.21 seconds
Rated: 313180.5 Bps, 2.50 Mbps, 542.83 pps
Actual: 13148 packets (7870783 bytes) sent in 25.26 seconds
Rated: 311561.9 Bps, 2.49 Mbps, 520.45 pps
Actual: 14500 packets (8612630 bytes) sent in 30.43 seconds
...
Actual: 24467 packets (14960314 bytes) sent in 110.83 seconds
Rated: 134978.5 Bps, 1.07 Mbps, 220.75 pps
Test complete: 2022-04-16 17:53:33.735188
Actual: 30023 packets (19277433 bytes) sent in 113.06 seconds
Rated: 170503.5 Bps, 1.36 Mbps, 265.54 pps
Statistics for network device: eth0
	Successful packets:        30023
	Failed packets:            0
	Truncated packets:         0
	Retried packets (ENOBUFS): 0
	Retried packets (EAGAIN):  0
```

And eventually we get a few alerts:

```shell
"2022-04-16T17:52:20.134763+0000,dns,1296231906414153,172.16.0.170:53806,172.16.0.52:53"
"2022-04-16T17:52:20.286785+0000,dns,293726410006593,172.16.0.170:50935,172.16.0.52:53"
"2022-04-16T17:52:20.290084+0000,dns,293726410006593,172.16.0.170:50935,172.16.0.52:53"
"2022-04-16T17:52:20.520858+0000,alert,1626224981242326,172.16.0.149:49795,172.16.0.52:139"
"2022-04-16T17:52:21.784804+0000,alert,1992149752477936,172.16.0.149:49796,172.16.0.52:139"
"2022-04-16T17:52:22.142041+0000,flow,1739064507071469,172.16.0.149:5353,224.0.0.251:5353"
"2022-04-16T17:52:22.351091+0000,dns,2078727703255923,172.16.0.149:51367,172.16.0.52:53"
"2022-04-16T17:52:22.351260+0000,dns,181632058678300,172.16.0.149:64943,172.16.0.52:53"
"2022-04-16T17:52:22.351129+0000,dns,2078727703255923,172.16.0.149:51367,172.16.0.52:53"
"2022-04-16T17:52:23.037637+0000,alert,282956779721256,172.16.0.149:49798,172.16.0.52:139"
"2022-04-16T17:52:23.901721+0000,dns,556717995180633,172.16.0.170:51164,172.16.0.52:53"
"2022-04-16T17:52:23.904764+0000,dns,556717995180633,172.16.0.170:51164,172.16.0.52:53"
"2022-04-16T17:52:24.293356+0000,alert,2006941620009246,172.16.0.149:49799,172.16.0.52:139"
"2022-04-16T17:52:25.322102+0000,dns,1671081620007478,172.16.0.170:51909,172.16.0.52:53"
```

For sake of example, zoom in alert id '282956779721256':

```json lines
// root@raspberrypi:~# grep 282956779721256 /var/log/suricata/eve.json|jq
{
  "timestamp": "2022-04-16T17:52:23.037637+0000",
  "flow_id": 282956779721256,
  "in_iface": "eth0",
  "event_type": "alert",
  "src_ip": "172.16.0.149",
  "src_port": 49798,
  "dest_ip": "172.16.0.52",
  "dest_port": 139,
  "proto": "TCP",
  "metadata": {
    "flowints": {
      "applayer.anomaly.count": 1
    }
  },
  "alert": {
    "action": "allowed",
    "gid": 1,
    "signature_id": 2260002,
    "rev": 1,
    "signature": "SURICATA Applayer Detect protocol only one direction",
    "category": "Generic Protocol Command Decode",
    "severity": 3
  },
  "smb": {
    "id": 1,
    "dialect": "NT LM 0.12",
    "command": "SMB1_COMMAND_NEGOTIATE_PROTOCOL",
    "status": "STATUS_SUCCESS",
    "status_code": "0x0",
    "session_id": 0,
    "tree_id": 0,
    "client_dialects": [
      "PC NETWORK PROGRAM 1.0",
      "LANMAN1.0",
      "Windows for Workgroups 3.1a",
      "LM1.2X002",
      "LANMAN2.1",
      "NT LM 0.12"
    ],
    "server_guid": "a21b9552-a4a0-48cd-8abb-ea111498253d"
  },
  "app_proto": "smb",
  "app_proto_ts": "failed",
  "flow": {
    "pkts_toserver": 4,
    "pkts_toclient": 3,
    "bytes_toserver": 579,
    "bytes_toclient": 387,
    "start": "2022-04-16T17:52:23.037416+0000"
  },
  "payload": "AAAAiv9TTUJzAAAAABgHyAAAQlNSU1BZTCAAAP////4AAEAADP8AAAAEQTIAAAAAAAAASgAAAAAA1AAAoE8AYEgGBisGAQUFAqA+MDygDjAMBgorBgEEAYI3AgIKoioEKE5UTE1TU1AAAQAAAJeCCOIAAAAAAAAAAAAAAAAAAAAACgBhSgAAAA8AAAAAAA==",
  "payload_printable": ".....SMBs.........BSRSPYL ........@.......A2.......J.........O.`H..+......>0<..0..\n+.....7..\n.*.(NTLMSSP.........................\n.aJ.........",
  "stream": 0,
  "packet": "AB5PDqh0ABv8e9HACABFAAC2t+tAAIAG6WysEACVrBAANMKGAIthfGQf7GIEdVAYIBP6YwAAAAAAiv9TTUJzAAAAABgHyAAAQlNSU1BZTCAAAP////4AAEAADP8AAAAEQTIAAAAAAAAASgAAAAAA1AAAoE8AYEgGBisGAQUFAqA+MDygDjAMBgorBgEEAYI3AgIKoioEKE5UTE1TU1AAAQAAAJeCCOIAAAAAAAAAAAAAAAAAAAAACgBhSgAAAA8AAAAAAA==",
  "packet_info": {
    "linktype": 1
  },
  "host": "ras[berripi"
}
{
  "timestamp": "2022-04-16T17:55:42.050329+0000",
  "flow_id": 282956779721256,
  "in_iface": "eth0",
  "event_type": "flow",
  "src_ip": "172.16.0.149",
  "src_port": 49798,
  "dest_ip": "172.16.0.52",
  "dest_port": 139,
  "proto": "TCP",
  "app_proto": "smb",
  "app_proto_ts": "failed",
  "flow": {
    "pkts_toserver": 13,
    "pkts_toclient": 12,
    "bytes_toserver": 1743,
    "bytes_toclient": 1963,
    "start": "2022-04-16T17:52:23.037416+0000",
    "end": "2022-04-16T17:52:23.488633+0000",
    "age": 0,
    "state": "closed",
    "reason": "timeout",
    "alerted": true
  },
  "metadata": {
    "flowbits": [
      "smb.tree.connect.ipc"
    ],
    "flowints": {
      "applayer.anomaly.count": 1
    }
  },
  "tcp": {
    "tcp_flags": "1b",
    "tcp_flags_ts": "1b",
    "tcp_flags_tc": "1b",
    "syn": true,
    "fin": true,
    "psh": true,
    "ack": true,
    "state": "closed"
  },
  "host": "raspberrypi"
}
```

That's quite a bit; keep in mind that while we are tuning Suricata, we can also ask it to replay one or more PCAP file directly

#### Ask Suricata to run in offline mode using PCAP file for SUNNYSTATION

It is a very convenient way to test Suricata, as we do not inject any traffic in our network and instead let Suricata 'ingest' the contents of the PCAP
file directly, to test the rules. Also, we redirect the logs to a separate location (by default the directory where you are running the 'offline' mode), so we don't pollute a live installation.

[![asciicast](https://asciinema.org/a/SH8bo3pjpvRt4H617GoHbPdoK.svg)](https://asciinema.org/a/SH8bo3pjpvRt4H617GoHbPdoK)


### Another example: EMOTET WITH COBALT STRIKE

Let's try another malware capture, in this case 2022-02-08 (TUESDAY) - [FILES FOR AN ISC DIARY (EMOTET WITH COBALT STRIKE)](https://www.malware-traffic-analysis.net/2022/02/08/index.html)

```shell
cd ~/Downloads/malware/ && \
curl --remote-name https://www.malware-traffic-analysis.net/2022/02/08/2022-02-08-Emotet-epoch4-infection-start-and-spambot-traffic.pcap.zip && \
unzip 2022-02-08-Emotet-epoch4-infection-start-and-spambot-traffic.pcap.zip && \
sudo suricata -r ~josevnz/Downloads/malware/2022-02-08-Emotet-epoch4-infection-start-and-spambot-traffic.pcap -k none --runmode autofp -c /etc/suricata/suricata.yaml -l ~josevnz/Downloads/malware/ 
```

Here is a sample session:

[![asciicast](https://asciinema.org/a/488035.svg)](https://asciinema.org/a/488035)

# Making sense of all the alerts

Suricata will save lots of details when it detects an anomaly; You can tell than using jq to go through the alerts may not be desirable.

For a bigger setup, you may want to use an [Elastic Stack](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-module-suricata.html) (Filebeat, Logstash, Elasticsearch, Kibana):
* Get the logs
* Store historically and normalize the logs
* Visualize their contents

But that feels overkill for a home setup, so I will roll a few scripts to help me with what I need.

## Show me what happened on the last 10 minutes

A script that assumes most of the defaults, so I don't have to type a jq expression. If there are any alerts then I dive deeper into the eve.json file.

A simple Python 3 script will do the trick for us:

```python
#!/usr/bin/env python
"""
Show Suricata alerts
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
"""
import argparse
import json
from datetime import datetime, timedelta
from json import JSONDecodeError
from pathlib import Path
from typing import Callable, Any, Dict

DEFAULT_EVE = [Path("/var/log/suricata/eve.json")]
DEFAULT_TIMESTAMP_10M_AGO = datetime = datetime.now() - timedelta(minutes=10)


def _parse_timestamp(candidate: str) -> datetime:
    """
    Expected something like 2022-02-08T16:32:14.900292+0000
    :param candidate:
    :return:
    """
    if isinstance(candidate, str):
        try:
            iso_candidate = candidate.split('+', 1)[0]
            return datetime.fromisoformat(iso_candidate)
        except ValueError:
            raise ValueError(f"Invalid date passed: {candidate}")
    elif isinstance(candidate, datetime):
        return candidate


def alert_filter(
        *,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO,
        data: Dict[str, Any]
) -> bool:
    if 'event_type' not in data:
        return False
    if data['event_type'] != 'alert':
        return False
    try:
        event_timestamp = _parse_timestamp(data['timestamp'])
        if event_timestamp > timestamp:
            return False
    except ValueError:
        return False
    return True


def get_alerts(
        *,
        eve_files=None,
        row_filter: Callable = alert_filter,
        timestamp: datetime = DEFAULT_TIMESTAMP_10M_AGO
) -> str:
    if eve_files is None:
        eve_files = DEFAULT_EVE
    for eve_file in eve_files:
        with open(eve_file, 'rt') as eve:
            for line in eve:
                try:
                    data = json.loads(line)
                    if row_filter(data=data, timestamp=timestamp):
                        yield data
                except JSONDecodeError:
                    continue  # Try to read the next record


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description=__doc__)
    PARSER.add_argument(
        "--timestamp",
        type=_parse_timestamp,
        default=DEFAULT_TIMESTAMP_10M_AGO,
        help=f"Minimum timestamp in the past to use when filtering events ({DEFAULT_TIMESTAMP_10M_AGO})"
    )
    PARSER.add_argument(
        'eve',
        type=Path,
        nargs="+",
        help=f"Path to one or more {DEFAULT_EVE[0]} file to parse."
    )
    OPTIONS = PARSER.parse_args()
    try:
        for alert in get_alerts(eve_files=OPTIONS.eve, timestamp=OPTIONS.timestamp):
            print(json.dumps(alert, indent=6, sort_keys=True))
    except KeyboardInterrupt:
        pass
```

It is a big improvement over jq as at least we can filter by timestamp, but It would be nice if our script could do the following:
1. Support pagination
2. Colorize output
3. Let you show between a table format or raw JSON output

[![asciicast](https://asciinema.org/a/488166.svg)](https://asciinema.org/a/488166)

# What did we learn and is next?

Suricata is a complex piece of software, it takes time to tame it and more time to make sense of the information it presents; But it is very rewarding to see how you can tackle a tool that will allow you to secure your network from threats.

* [The OISF Suricata YouTube channel](https://www.youtube.com/c/OISFSuricata) has many interesting resources about this tool and a thriving community.
* Want to learn how to analyze PCAP files for bad traffic? [malware-traffic-analysis](https://www.malware-traffic-analysis.net/training-exercises.html) has perfect material for you.
* **Writing complex software is hard**. For example, older versions of Snort are vulnerable to an [attack that can disable it, CVE-2022-20685](https://claroty.com/2022/04/14/blog-research-blinding-snort-breaking-the-modbus-ot-preprocessor/); Suricata also had [CVE-2019-1010279](https://nvd.nist.gov/vuln/detail/CVE-2019-1010279) 
These issues were fixed but illustrates the need to keep your software current, specially the one you use to protect your network. 
* I did not touch the IPS mode, or even hybrid modes for Suricata. Please read the official documentation to get up to speed.
* Finally, do yourself a favor and read this [Suricata Tutorial from FloCon 2016](https://resources.sei.cmu.edu/asset_files/Presentation/2016_017_001_449890.pdf); It is very complete and will have you looking for more.

Please leave your comments on the git repository and report any bugs. But more important get Suricata, [get the code of this tutorial](https://github.com/josevnz/SuricataLog), and start securing your home wireless infrastructure in no time.
