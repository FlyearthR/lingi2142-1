""" This python script checks if the BGP connection is working, and sends an snmp TRAP
if the connection is broken.
"""
import subprocess
import shlex
import re

# Use socket and DNSpython to monitor the state of DNS 
import socket
import dns.resolver

""" CONSTANTS """
# GENERAL
CFG_FILE_PATH = '/etc/scripts/trapnotifier.conf'

# SNMPTRAP
VERSION = '2c'
COMMUNITY = 'public' 
MONITOR_IPs = ['fe80::89e:b7ff:fe0d:3016', '::1']    # IPs of the monitoring servers
UPTIME = ''                 # Let the agent set the uptime

# DNS
NAME_SERVERS = ['', '']
TARGET = 'www.uclouvain.be'



""" FUNCTIONS """

def send_traps(oid, object_type, value_type, value):
    for monitor_ip in MONITOR_IPs:
            subprocess.call(['snmptrap', '-v', VERSION, '-c', COMMUNITY, monitor_ip, UPTIME, oid, object_type, value_type, value])

# TEST DNS (ONLY MONITORING SERVERS?)
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
                print(rdata.target)
        except dns.exception.DNSException as e:
            send_traps(oid, object_type, value_type, str(e))

# TEST BGP (PYTHAGORE AND HALLES)
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
            if state == 'up' :
                value = 'BGP - '+server_name+': protocol status -> '+state
                send_traps(oid, object_type, value_type, value)
                print(value)
            elif info != 'established':
                value = 'BGP - '+server_name+': BGP connection '+info
                send_traps(oid, object_type, value_type, value)
                print(value)
            print('BGP connection '+info)



# TEST OSPF (EACH NODE MUST DO IT!)
def check_ospf(server_name):
    oid = '1.3.6.1.3.19997.0.0.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.ospfNeighbourUnavailableNotification
    object_type = '1.3.6.1.3.19997.0.1.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.ospfNeighbourUnavailable
    value_type = 's'
    # Test if OSPF works
    p1 = subprocess.Popen(shlex.split('printf "show ospf neighbors\nquit\n"'), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split('birdc6 -s /tmp/'+server_name+'_bird6.ctl'), stdin=p1.stdout, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    out = out.decode('utf-8')
    for l in out.splitlines()[5:-1]:
        neighbor = l.split()
        print(neighbor)
        neighbor_state = neighbor[2]
        neighbor_interface = neighbor[4]
        neighbor_ip = neighbor[5]
        ns = neighbor_state.split('/')[0].lower()
        if ns not in ['full', '2way']:
            value = 'OSPF - '+server_name+': neighbor @'+neighbor_ip+' '+ns
            send_traps(oid, object_type, value_type, value)
            print('Neighbor @'+neighbor_ip+' '+ns)
        else:
            print('Neighbor @'+neighbor_ip+' up!')
    # CHECK if number of neighbors == expected number ?


# Read server name + execute functions
with open(CFG_FILE_PATH, 'r') as f:
    server_name = f.readline().rstrip('\n')
    for line in f:
        globals()['check_'+line.rstrip('\n')](server_name)
