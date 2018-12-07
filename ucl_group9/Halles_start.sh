#!/bin/bash

puppet apply --detailed-exitcodes --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip -6 tunnel add tun mode ip6ip6 remote "${PREFIXBASE_as300}:2600::3" local "${PREFIXBASE_as300}:2100::3"
ip -6 link set tun up


ip address add dev Halles-eth0 "${PREFIXBASE_as200}:2100::0"
ip address add dev Halles-eth1 "${PREFIXBASE_as200}:2100::1"
ip address add dev Halles-eth0 "${PREFIXBASE_as300}:2100::0"
ip address add dev Halles-eth1 "${PREFIXBASE_as300}:2100::1"
ip address add dev tun "${PREFIXBASE_as300}:2100::3"

ip address add dev Halles-lan0 "${PREFIXBASE_as200}:2101::/$((PREFIXLEN+16))"
ip address add dev Halles-lan0 "${PREFIXBASE_as300}:2101::/$((PREFIXLEN+16))"

ip -6 rule add from "${PREFIXBASE_as300}::/${PREFIXLEN}" to "${PREFIXBASE_as200}::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as300}::/${PREFIXLEN}" to "${PREFIXBASE_as300}::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as300}::/${PREFIXLEN}" to "fd00:200:1::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as300}::/${PREFIXLEN}" to "fd00:300:1::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as300}::/${PREFIXLEN}" table 9 pref 200
ip route add ::/0 dev tun table 9

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/traplistener.py > /etc/monitoring_logs.txt 2>&1 &
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/agentmonitor.py > /etc/monitoring_logs.txt 2>&1 & 
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
