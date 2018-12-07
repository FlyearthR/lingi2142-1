#!/bin/bash

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev NS2-eth0 "${PREFIXBASE_as200}:2101::2/64"
ip address add dev NS2-eth0 "${PREFIXBASE_as300}:2101::2/64"

ip route add ::/0 via "${PREFIXBASE_as300}:2101::" dev NS2-eth0
ip route add "${PREFIXBASE_as200}::/${PREFIXLEN}" via "${PREFIXBASE_as200}:2101::" dev NS2-eth0

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &

