#!/bin/bash

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev NS1-eth0 "${PREFIXBASE_as200}:2401::2/$((PREFILEN+16))"
ip address add dev NS1-eth0 "${PREFIXBASE_as300}:2401::2/$((PREFILEN+16))"

ip route add ::/0 via "${PREFIXBASE_as300}:2401::" dev NS1-eth0
ip route add "${PREFIXBASE_as200}::/48" via "${PREFIXBASE_as200}:2401::" dev NS1-eth0

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
