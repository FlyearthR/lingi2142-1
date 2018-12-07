#!/usr/bin/python3
""" This python script checks if everything is working correctly, and sends an snmp TRAP otherwise."""
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
MONITOR_IPs = ['fd00:200:9:2401::1', 'fd00:200:9:2101::1']    # IPs of the monitoring servers
UPTIME = ''                 # Let the agent set the uptime

# DNS
NAME_SERVERS = ['fd00:200:9:2401::2', 'fd00:200:9:2101::2']
TARGET = 'uclouvain.be'


class Trapnotifiers:
    def __init__(self, server_name, fun_names):
        self.ospf_neighbors = []
        self.server_name = server_name
        self.functions = []
        for fun_name in fun_names:
            print(fun_name)
            if fun_name == "dns":
                self.functions.append(self.check_dns)
            elif fun_name == "bgp":
                self.functions.append(self.check_bgp)
            elif fun_name == "ospf":
                self.functions.append(self.check_ospf)

    def call_functions(self):
        for fun in self.functions:
            fun()

    def send_traps(self, oid, object_type, value_type, value):
        """Sends a trap to each monitoring server, with the parameters given as argument"""
        print('sending trap')
        for monitor_ip in MONITOR_IPs:
            subprocess.call(['snmptrap', '-v', VERSION, '-c', COMMUNITY, monitor_ip, UPTIME, oid, object_type, value_type, '[%s] %s' % (self.server_name, value)])

    def check_dns(self):
        """Checks if the DNS servers are working correctly. Sends a trap to the monitoring
        servers if that's not the case"""
        oid = '1.3.6.1.3.19997.0.0.0' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.dnsDownNotification
        object_type = '1.3.6.1.3.19997.0.1.0' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.dnsDown
        value_type = 's'
        for nameServer in NAME_SERVERS:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            resolver.nameservers = [nameServer]
            try:
                for rdata in resolver.query(TARGET) :
                    print('DNS OK')
                    pass
            except dns.exception.DNSException as e:
                value = 'NS: {} {}'.format(nameServer, str(e))
                print(value)
                self.send_traps(oid, object_type, value_type, 'NS: ' + nameServer + ' ' + str(e))

    def check_bgp(self):
        """Checks if the BGP connections are up. Sends a trap to the monitoring
        servers if that's not the case"""
        oid = '1.3.6.1.3.19997.0.0.1' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.bgpErrorNotification
        object_type = '1.3.6.1.3.19997.0.1.1' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.bgpError
        value_type = 's'
        # Test if BGP session is up
        p1 = subprocess.Popen(shlex.split('printf "show protocols\nquit\n"'), stdout=subprocess.PIPE)
        p2 = subprocess.Popen(shlex.split('birdc6 -s /tmp/'+self.server_name+'_bird6.ctl'), stdin=p1.stdout, stdout=subprocess.PIPE)
        out, err = p2.communicate()
        out = out.decode('utf-8')
        for l in out.splitlines()[5:-1]:
            protocol = l.split()
            if protocol[1].lower() == 'bgp':
                state = protocol[3].lower()
                info = protocol[5].lower()
                if state != 'up' :
                    value = 'BGP - {}: protocol status -> {}'.format(self.server_name, state)
                    self.send_traps(oid, object_type, value_type, value)
                    print(value)
                elif info != 'established':
                    value = 'BGP - {}: BGP connection {}'.format(self.server_name, info)
                    self.send_traps(oid, object_type, value_type, value)
                    print(value)
                print('BGP connection '+info)

    def check_ospf(self):
        """Checks if the network nodes are correctly connected together. Sends a trap to the monitoring
        servers if that's not the case"""
        oid = '1.3.6.1.3.19997.0.0.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.prefix.ospfNeighbourUnavailableNotification
        object_type = '1.3.6.1.3.19997.0.1.2' # Experimental OID : SNMPv2-SMI::experimental.group9.notifications.objects.ospfNeighbourUnavailable
        value_type = 's'
        # Test if OSPF works
        p1 = subprocess.Popen(shlex.split('printf "show ospf neighbors\nquit\n"'), stdout=subprocess.PIPE)
        p2 = subprocess.Popen(shlex.split('birdc6 -s /tmp/'+self.server_name+'_bird6.ctl'), stdin=p1.stdout, stdout=subprocess.PIPE)
        out, err = p2.communicate()
        out = out.decode('utf-8')
        neighbor_infos = []
        for l in out.splitlines()[5:-1]:
            neighbor = l.split()
            neighbor_state = neighbor[2]
            neighbor_interface = neighbor[4]
            neighbor_ip = neighbor[5]
            neighbor_infos.append((neighbor_interface, neighbor_ip))
            ns = neighbor_state.split('/')[0].lower()
            if ns not in ['full', '2way']:
                value = 'OSPF - {}: neighbor @{} {}!'.format(self.server_name, neighbor_ip, ns)
                self.send_traps(oid, object_type, value_type, value)
                print(value)
            else:
                pass
                print('Neighbor @{} up!'.format(neighbor_ip))
        # List of the new neighbors compared to the previous execution of the function
        new_neighbors = [x for x in neighbor_infos if x not in self.ospf_neighbors]
        # List of the unavailable neighbors compared to the previous execution of the function
        unavailable_neigbors = [x for x in self.ospf_neighbors if x not in neighbor_infos]
        # Send traps if neighbors became unavailable + update list of neighbors
        if len(unavailable_neigbors) > 0:
            self.ospf_neighbors = [x for x in self.ospf_neighbors if x in neighbor_infos]
            for interface, ip in unavailable_neigbors:
                value = 'OSPF - {0}: Neighbor at interface {1} unreachable!'.format(self.server_name, interface)
                self.send_traps(oid, object_type, value_type, value)
                print(value)
        # Send traps if there are new neighbors + update list of neighbors
        if len(new_neighbors) > 0:
            self.ospf_neighbors.extend(new_neighbors)
            for interface, ip in new_neighbors:
                value = 'OSPF - {0}: Neighbor at interface {1} became reachable @{2}!'.format(self.server_name, interface, ip)
                self.send_traps(oid, object_type, value_type, value)
                print(value)


# Read server name + execute functions
with open(CFG_FILE_PATH, 'r') as f:
    content = f.readlines()
    server_name = content[0].rstrip('\n')
    functions = [fun_name.strip() for fun_name in content[1:]]
    trap = Trapnotifiers(server_name, functions)
    while True:
        print('running')
        trap.call_functions()
        time.sleep(15)
