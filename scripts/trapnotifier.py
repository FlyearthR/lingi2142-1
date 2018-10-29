#!/usr/bin/python3
""" This python script checks if the BGP connection is working, and sends an snmp TRAP
if the connection is broken.
"""
import subprocess
import shlex
import re
import time

# Use socket and DNSpython to monitor the state of DNS 
import socket
import dns.resolver

""" CONSTANTS """
# GENERAL
CFG_FILE_PATH = '/etc/scripts/trapnotifier.conf'

# SNMPTRAP
VERSION = '2c'
COMMUNITY = 'public' 
MONITOR_IPs = ['fd00:200:9:2400::1', 'fd00:200:9:2100::1', 'fd00:300:9:2000::100']    # IPs of the monitoring servers
UPTIME = ''                 # Let the agent set the uptime

# DNS
NAME_SERVERS = ['fd00:200:9:2400::2', 'fd00:200:9:2100::2']
TARGET = 'www.uclouvain.be'



""" FUNCTIONS """

def send_traps(oid, object_type, value_type, value, server_name):
    print('sending trap')
    for monitor_ip in MONITOR_IPs:
        subprocess.call(['snmptrap', '-v', VERSION, '-c', COMMUNITY, monitor_ip, UPTIME, oid, object_type, value_type, '[%s] %s' % (server_name, value)])

# TEST DNS 
def check_dns(server_name):
    oid = '1.3.6.1.3.19997.0.0.0' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.dnsDownNotification
    object_type = '1.3.6.1.3.19997.0.1.0' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.dnsDown
    value_type = 's'
    for nameServer in NAME_SERVERS:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 5
        resolver.lifetime = 5
        resolver.nameservers=[nameServer]
        try:
            for rdata in resolver.query(TARGET, 'CNAME') :
                #print(rdata.target)
                pass
        except dns.exception.DNSException as e:
            send_traps(oid, object_type, value_type, 'NS: ' + nameServer + ' ' + str(e), server_name)

# TEST BGP 
def check_bgp(server_name):
    oid = '1.3.6.1.3.19997.0.0.1' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.bgpErrorNotification
    object_type = '1.3.6.1.3.19997.0.1.1' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.bgpError
    value_type = 's'
    # Test if BGP session is up
    p1 = subprocess.Popen(shlex.split('printf "show protocols\nquit\n"'), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split('birdc6 -s /tmp/'+server_name+'_bird6.ctl'), stdin=p1.stdout, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    out = out.decode('utf-8')
    for l in out.splitlines()[5:-1]:
        protocol = l.split()
        if protocol[1].lower() == 'bgp':
            state = protocol[3].lower()
            info = protocol[5].lower()
            if state != 'up' :
                value = 'BGP - '+server_name+': protocol status -> '+state
                send_traps(oid, object_type, value_type, value, server_name)
                #print(value)
            elif info != 'established':
                value = 'BGP - '+server_name+': BGP connection '+info
                send_traps(oid, object_type, value_type, value, server_name)
                #print(value)
            #print('BGP connection '+info)



# TEST OSPF
def check_ospf(server_name):
    oid = '1.3.6.1.3.19997.0.0.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.ospfNeighbourUnavailableNotification
    object_type = '1.3.6.1.3.19997.0.1.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.ospfNeighbourUnavailable
    value_type = 's'
    # Test if OSPF works
    p1 = subprocess.Popen(shlex.split('printf "show ospf neighbors\nquit\n"'), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split('birdc6 -s /tmp/'+server_name+'_bird6.ctl'), stdin=p1.stdout, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    out = out.decode('utf-8')
    for l in out.splitlines()[6:-1]:
        neighbor = l.split()
        neighbor_state = neighbor[2]
        neighbor_interface = neighbor[4]
        neighbor_ip = neighbor[5]
        ns = neighbor_state.split('/')[0].lower()
        if ns not in ['full', '2way']:
            value = 'OSPF - '+server_name+': neighbor @'+neighbor_ip+' '+ns
            send_traps(oid, object_type, value_type, value, server_name)
            #print('Neighbor @'+neighbor_ip+' '+ns)
        else:
            pass
            #print('Neighbor @'+neighbor_ip+' up!')
    # CHECK if number of neighbors == expected number ?


# Read server name + execute functions
with open(CFG_FILE_PATH, 'r') as f:
    content = f.readlines()
server_name = content[0].rstrip('\n')
while True:
    print('running')
    for line in content[1:]:
        globals()['check_'+line.rstrip('\n')](server_name)
    time.sleep(30)
