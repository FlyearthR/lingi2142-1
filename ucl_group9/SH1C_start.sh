#!/bin/bash

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules
wait
source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev SH1C-eth0 "${PREFIXBASE_as200}:2200::0"
ip address add dev SH1C-eth1 "${PREFIXBASE_as200}:2200::1"
ip address add dev SH1C-eth0 "${PREFIXBASE_as300}:2200::0"
ip address add dev SH1C-eth1 "${PREFIXBASE_as300}:2200::1"

ip address add dev SH1C-lan0 "${PREFIXBASE_as300}:1200::/$((PREFIXLEN+16))"

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
