#!/bin/bash

# ip address add dev ART-eth0 fd00:300:9:0300::1/64

# ip -6 route add ::/0 via fd00:300:9:0300:: dev ART-eth0

puppet apply --verbose --parser future --hiera_config=/etc/puppet/hiera.yaml /etc/puppet/site.pp --modulepath=/puppetmodules
wait

source "$(cd "$(dirname "$0")"; pwd -P)/../ucl_topo"

#ip address add dev SH2-eth0 "${PREFIXBASE_as200}:1200::2/64"
#ip address add dev SH2-eth0 "${PREFIXBASE_as300}:1200::2/64"

#ip route add via "${PREFIXBASE_as300}:1200::" dev SH2-eth0 ::/0
#ip route add via "${PREFIXBASE_as200}:1200::" dev SH2-eth0 "${PREFIXBASE_as200}::/${PREFIXLEN}"
