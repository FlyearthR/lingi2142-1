#!/bin/bash

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

ip address add dev MO1-eth0 "${PREFIXBASE_as200}:2401::1/64"
ip address add dev MO1-eth0 "${PREFIXBASE_as300}:2401::1/64"

ip route add via "${PREFIXBASE_as300}:2401::" dev MO1-eth0 ::/0
ip route add via "${PREFIXBASE_as200}:2401::" dev MO1-eth0 "${PREFIXBASE_as200}::/${PREFIXLEN}"

wait

nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/traplistener.py > /etc/monitoring_logs.txt 2>&1 &
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/agentmonitor.py > /etc/monitoring_logs.txt 2>&1 & 
nohup /usr/bin/python3 /home/vagrant/lingi2142-1/scripts/trapnotifier.py > /etc/trap_notifier_logs.txt 2>&1 &
