#!/bin/bash

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev Carnoy-eth0 "${PREFIXBASE_as200}:2000::400"
ip address add dev Carnoy-eth1 "${PREFIXBASE_as200}:2000::401"
ip address add dev Carnoy-eth2 "${PREFIXBASE_as200}:2000::402"
ip address add dev Carnoy-eth0 "${PREFIXBASE_as300}:2000::400"
ip address add dev Carnoy-eth1 "${PREFIXBASE_as300}:2000::401"
ip address add dev Carnoy-eth2 "${PREFIXBASE_as300}:2000::402"

ip address add dev Carnoy-lan0 "${PREFIXBASE_as200}:e::/$((PREFIXLEN+16))"
ip address add dev Carnoy-lan1 "${PREFIXBASE_as200}:2400::/$((PREFIXLEN+16))"
ip address add dev Carnoy-lan1 "${PREFIXBASE_as300}:2400::/$((PREFIXLEN+16))"

ip route add dev Carnoy-lan0 "${PREFIXBASE_as200}:e::/$((PREFIXLEN+16))"
ip route add dev Carnoy-lan1 "${PREFIXBASE_as200}:2400::/$((PREFIXLEN+16))"
ip route add dev Carnoy-lan1 "${PREFIXBASE_as300}:2400::/$((PREFIXLEN+16))"

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
