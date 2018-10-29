#!/bin/bash

puppet apply --detailed-exitcodes --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev Halles-eth0 "${PREFIXBASE_as200}:2000::100"
ip address add dev Halles-eth1 "${PREFIXBASE_as200}:2000::101"
ip address add dev Halles-eth0 "${PREFIXBASE_as300}:2000::100"
ip address add dev Halles-eth1 "${PREFIXBASE_as300}:2000::101"

ip address add dev Halles-lan0 "${PREFIXBASE_as200}:2100::/$((PREFIXLEN+16))"
ip address add dev Halles-lan0 "${PREFIXBASE_as300}:2100::/$((PREFIXLEN+16))"

ip route add dev Halles-lan0 "${PREFIXBASE_as200}:2100::/$((PREFIXLEN+16))"
ip route add dev Halles-lan0 "${PREFIXBASE_as300}:2100::/$((PREFIXLEN+16))"

ip route add blackhole "${PREFIXBASE_as300}::/50"
ip route add blackhole "${PREFIXBASE_as200}::/50"

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/traplistener.py > /etc/monitoring_logs.txt 2>&1 &
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/agentmonitor.py > /etc/monitoring_logs.txt 2>&1 & 
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
