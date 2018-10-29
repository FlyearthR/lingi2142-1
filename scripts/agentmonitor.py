#!/usr/bin/python3
import os, time, signal
from random import random
# PySNMP High Level API. Commands: bulkCmd, getCmd, nextCmd and setCmd
from pysnmp.hlapi import *
# Data types used by PySNMP
from pyasn1.type.univ import * 
# Multithreading
import threading
# SNMP getter functions
from snmpfun import *

# Path to the config file
CFG_FILE_PATH = '/etc/scripts/agent_list.conf'

# Port
SNMP_PORT = 161 

# Path to the monitoring data
SNMP_LOG_PATH = '/etc/monitoring'

# SNMPv3 user
SNMPv3_USER = {   
                'userName': 'arthur', 
                'authProtocol': usmHMACSHAAuthProtocol, # SHA (128bit)
                'authKey': 'password',
                'privKey': 'secret_key',
                'privProtocol': usmAesCfb128Protocol # AES (128bit)
            }

# Monitoring parameters
TIME_INTERVAL = 300 
TIME_WAIT_VALUE = 330

class FunctionThread(threading.Thread):
    """A thread that runs a function with its arguments"""
    def __init__(self, function, *args):
        threading.Thread.__init__(self)
        self._function = function
        self._args = args
    
    def run(self):
        self._function(*self._args)

class MonitoringExit(Exception):
    """Custom exception that is thrown when stopping monitoring"""
    pass

def monitoring_shutdown(signum, frame):
    """Signal handler function"""
    raise MonitoringExit

def agent_monitor(stop_event, ips, snmp_port, db_directory, time_interval, snmpv3_user, data_collect_funs):
    """Monitors an agent by regularly sending snmp get requests"""
    stop_event.wait(180)
    # Instantiate SNMP engine
    snmp_engine = SnmpEngine()

    # Instantiate user - SNMPv3
    user = UsmUserData(**snmpv3_user)

    # Instantiate transport protocol (UDP over IPv6)
    upd_targets = [Udp6TransportTarget((ip, snmp_port), timeout=2) for ip in ips] 

    while not stop_event.is_set():
        for data_collect_fun in data_collect_funs:
            data_collect_fun(snmp_engine, user, upd_targets, db_directory)
        # Wait before getting next data
        stop_event.wait(time_interval)    

def main():
    threads = []
    stop_event = threading.Event()

    # Set signals handlers
    signal.signal(signal.SIGTERM, monitoring_shutdown)
    signal.signal(signal.SIGINT, monitoring_shutdown)

    # Initiate monitoring threads
    with open(CFG_FILE_PATH, 'r') as f:
        for line in f:
            agent_name, *agent_ips = line.split()
            print(agent_ips)
            db_directory = os.path.join(SNMP_LOG_PATH, agent_name)
            # Create DB directory
            if not os.path.exists(db_directory):
                os.makedirs(db_directory)
            # Initialize database
            initialize_ip_info_db(db_directory, TIME_INTERVAL, TIME_WAIT_VALUE)
            # Monitored items
            monitored_items = [ip_info]
            # Add thread to list of threads
            threads.append(FunctionThread(agent_monitor, stop_event, agent_ips, SNMP_PORT, db_directory, TIME_INTERVAL, SNMPv3_USER, monitored_items))
    
    try:
        # Start each thread
        for th in threads:
            th.start()
        # Keep this thread active, in order to cleanly stop each thread
        while True:
            time.sleep(1)

    except MonitoringExit:
        # Stop each thread
        stop_event.set()
        for th in threads:
            th.join()

main()
