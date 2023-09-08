#!/bin/bash
:<<DOC
Script to replay a PCAP file at accelerated pace on the default network interface
This script is meant to be used for testing; Also you can tell Suricata to replay any pcap file by itself using the
offline mode (-r \$pcapfile).
As usual be careful with what you decide to replay on your network.
Author: Jose Vicente Nunez (kodegeek.com@protonmail.com)
DOC
MULTIPLIER=24
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
    if ! tcpreplay --stats 5 --intf1 "$default_dev" --multiplier "$MULTIPLIER" "$pcap"; then
      echo "ERROR: Will not try to replay any pending PCAP files due previous errors"
      exit 100
    fi
  fi
done