#!/bin/bash

puppet apply --verbose --detailed-exitcodes --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules
wait
source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip -6 tunnel add tun mode ip6ip6 remote "${PREFIXBASE_as300}:2100::3" local "${PREFIXBASE_as300}:2600::3"
ip -6 link set tun up


ip address add dev Pythagore-eth0 "${PREFIXBASE_as200}:2600::0"
ip address add dev Pythagore-eth1 "${PREFIXBASE_as200}:2600::1"
ip address add dev Pythagore-eth2 "${PREFIXBASE_as200}:2600::2"
ip address add dev Pythagore-eth0 "${PREFIXBASE_as300}:2600::0"
ip address add dev Pythagore-eth1 "${PREFIXBASE_as300}:2600::1"
ip address add dev Pythagore-eth2 "${PREFIXBASE_as300}:2600::2"
ip address add dev tun "${PREFIXBASE_as300}:2600::3"
ip route add dev tun "${PREFIXBASE_as300}:2600::3"

ip address add dev Pythagore-lan0 "${PREFIXBASE_as300}:5600::/$((PREFIXLEN+16))"
ip address add dev Pythagore-lan0 "${PREFIXBASE_as200}:5600::/$((PREFIXLEN+16))"

ip -6 rule add from "${PREFIXBASE_as200}::/${PREFIXLEN}" to "${PREFIXBASE_as200}::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as200}::/${PREFIXLEN}" to "${PREFIXBASE_as300}::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as200}::/${PREFIXLEN}" to "fd00:200:1::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as200}::/${PREFIXLEN}" to "fd00:300:1::/${PREFIXLEN}" table main pref 100
ip -6 rule add from "${PREFIXBASE_as200}::/${PREFIXLEN}" table 9 pref 200
ip route add ::/0 dev tun table 9

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
