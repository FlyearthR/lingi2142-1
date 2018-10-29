#!/bin/bash

puppet apply --verbose --detailed-exitcodes --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules
wait
source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev Pythagore-eth0 "${PREFIXBASE_as200}:2000::600"
ip address add dev Pythagore-eth1 "${PREFIXBASE_as200}:2000::601"
ip address add dev Pythagore-eth2 "${PREFIXBASE_as200}:2000::602"
ip address add dev Pythagore-eth0 "${PREFIXBASE_as300}:2000::600"
ip address add dev Pythagore-eth1 "${PREFIXBASE_as300}:2000::601"
ip address add dev Pythagore-eth2 "${PREFIXBASE_as300}:2000::602"

ip address add dev Pythagore-lan0 "${PREFIXBASE_as300}:5600::/$((PREFIXLEN+16))"
ip route add dev Pythagore-lan0 "${PREFIXBASE_as300}:5600::/$((PREFIXLEN+16))"

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
