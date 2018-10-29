import os, sys, time
# PySNMP High Level API. Commands: bulkCmd, getCmd, nextCmd and setCmd
from pysnmp.hlapi import *
from pysnmp.smi.view import MibViewController
# Data types used by PySNMP
from pyasn1.type.univ import * 
# PySnmpError
from pysnmp.error import PySnmpError
# Round-Robin Database 
import rrdtool 

"""USEFUL FUNCTIONS"""
def update_rrd(snmp_engine, user, upd_target, data, db_location, file_location):
    """Updates the database given as argument with the data received in response to an SNMP GET request"""
    try:
        # Get data from agent
        get_data = getCmd(snmp_engine, user, upd_target, ContextData(), *data)
        errorIndication, errorStatus, errorIndex, varBinds = next(get_data)
        # Get current time
        if errorIndication:
            return 'ERROR:\n%s' % errorIndication
        elif errorStatus:
            return 'ERROR\n%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?')
        else:
            # If no error has occurred, write data in file and in database
            rrd_cmd='N'
            with open(file_location, 'a+') as f:
                t = time.gmtime()
                f.write("SNMP DATA received on %s:\n" % time.strftime('%c', t))
                for name, val in varBinds:
                    f.write('%s = %s\n' % (name.prettyPrint(), val.prettyPrint()))
                    rrd_cmd += ':' + val.prettyPrint()
                rrdtool.update(db_location, rrd_cmd)
            return 'DATA_OK'
    except PySnmpError as err:
        return 'ERROR:\n %s' % str(err)


"""INITIALIZATION FUNCTIONS"""
def initialize_ip_info_db(directory, time_interval, time_wait_value):
    """Initialises the rrd and the log file"""
    db_location = os.path.join(directory, 'ip.rrd')
    file_location = os.path.join(directory, 'ip.txt')
    # Create txt log file
    os.umask(0)
    open(os.open(file_location, os.O_CREAT | os.O_WRONLY, 0o777), 'w+').close()
    # Create round-robin database
    rrdtool.create( db_location, 
                    '--start', 'now', 
                    '--step', str(time_interval), 
                    'DS:received:COUNTER:'+str(time_wait_value)+':0:U',
                    'DS:delivered:COUNTER:'+str(time_wait_value)+':0:U',
                    'DS:forwarded:COUNTER:'+str(time_wait_value)+':0:U', 
                    'RRA:AVERAGE:0.5:1:100')

"""DATA COLLECTION FUNCTIONS"""
def ip_info(snmp_engine, user, upd_targets, directory):
    """Collects information about the IP packets going through this agent's interfaces"""
    db_location = os.path.join(directory, 'ip.rrd')
    file_location = os.path.join(directory, 'ip.txt')
    data = (
        ObjectType(ObjectIdentity('IP-MIB', 'ipInReceives', 0)), # Total number of received input datagrams (including those received in error)
        ObjectType(ObjectIdentity('IP-MIB', 'ipInDelivers', 0)), # Total number of input datagrams successfully delivered to IP user protocols
        ObjectType(ObjectIdentity('IP-MIB', 'ipForwDatagrams', 0)) # Number of input datagrams for which this entity was not their final IP destination
    )
    i = 0
    msg = ''
    while i < len(upd_targets) and msg != 'DATA_OK':
        msg = update_rrd(snmp_engine, user, upd_targets[i], data, db_location, file_location)   ############################
        i += 1
    if msg != 'DATA_OK':
        print('Unable to get snmp data from agent: %s' % msg, file=sys.stderr)

