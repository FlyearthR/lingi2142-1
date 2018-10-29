#!/bin/bash

#tests the bgp peering and network accessability


if [[ "$UID" != "0" ]]; then
    echo "This script must be run as root!"
    exit 1
fi


/usr/bin/printf "show protocols all\nquit\n" | birdc6 -s /tmp/Halles_bird6.ctl | grep -A4 BGP  | egrep "^R|Routes"
