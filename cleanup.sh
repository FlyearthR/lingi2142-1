#!/bin/bash

if [[ "$UID" != "0" ]]; then
    echo "This script must be run as root!"
    exit 1
fi

_dname=$(dirname "$0")
BDIR=$(cd "$_dname"; pwd -P)
# Get config-specific settings (i.e. to override GROUPNUMBER)
_settings="${BDIR}/settings"
if [ -x "$_settings" ]; then
    source "$_settings"
fi

echo 'Destroying the root bridges'
# Gracefully disconnect from the bridge in the root namespace (if any)
for i in eth1\
         eth2; do
    # Destroy slave of "br$i" because it does not always get destroyed
    slave=$(ip link | grep "\-$i" | cut -d ":" -f 2 | cut -c 2-)
    if ! [ -z "${slave}" ]; then
        ip link del dev "${slave}"
    fi
    ip link del dev "br$i" &> /dev/null
done

# Cleanup all network namespaces
for ns in $(ip netns list) ; do
    echo "Killing namespace $ns"
    # Kill all processes running in the namespaces
    # First SIGTERM
    ip netns pids "$ns" | xargs '-I{}' kill '{}'
    sleep .05
    # Then SIGKILL
    ip netns pids "$ns" | xargs '-I{}' kill -s 9 '{}'
    # Destroy the net NS --- All interfaces/bridges will be destroyed alongside
    ip netns del "$ns"
    rm -rf ucl_group9/"$ns"/snmp
    rm -rf ucl_group9/"$ns"/monitoring
    rm -rf ucl_group9/"$ns"/cron.d
    rm -rf ucl_group9/"$ns"/scripts
    rm -rf monitoring_data
    rm -f ucl_group9/"$ns"/monitoring_logs.txt
done

# Destroy bird/zebra temp files
rm -f /tmp/*.{api,ctl}

pkill -u root cron
