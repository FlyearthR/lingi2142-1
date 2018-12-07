# https://oss.oetiker.ch/rrdtool/tut/rrd-beginners.en.html
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
            t = time.gmtime()
            if file_location is not None:
                with open(file_location, 'a+') as f:
                    f.write("SNMP DATA received on %s:\n" % time.strftime('%c', t))
                    for name, val in varBinds:
                        f.write('%s = %s\n' % (name.prettyPrint(), val.prettyPrint()))
                        rrd_cmd += ':' + val.prettyPrint()
                    rrdtool.update(db_location, rrd_cmd)
            else:
                for name, val in varBinds:
                    rrd_cmd += ':' + val.prettyPrint()
                rrdtool.update(db_location, rrd_cmd)
            return 'DATA_OK'
    except PySnmpError as err:
        return 'ERROR:\n %s' % str(err)
    except Exception as err:
        return 'ERROR:\n %s' % str(err)


"""INITIALIZATION FUNCTIONS"""
def initialize_ip_info_db(directory, time_interval, time_wait_value, txt_backup=False):
    """Initialises the rrd and the log file"""
    db_location = os.path.join(directory, 'ip.rrd')
    if txt_backup:
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
                    'RRA:AVERAGE:0.5:1:8640')

def initialize_ram_info_db(directory, time_interval, time_wait_value, txt_backup=False):
    """Initialises the rrd and the log file"""
    db_location = os.path.join(directory, 'ram_usage.rrd')
    if txt_backup:
        file_location = os.path.join(directory, 'ram_usage.txt')
        # Create txt log file
        os.umask(0)
        open(os.open(file_location, os.O_CREAT | os.O_WRONLY, 0o777), 'w+').close()
    # Create round-robin database
    rrdtool.create( db_location, 
                    '--start', 'now', 
                    '--step', str(time_interval), 
                    'DS:used:GAUGE:'+str(time_wait_value)+':0:U',
                    'DS:free:GAUGE:'+str(time_wait_value)+':0:U', 
                    'RRA:AVERAGE:0.5:1:100')

def initialize_cpu_info_db(directory, time_interval, time_wait_value, txt_backup=False):
    """Initialises the rrd and the log file"""
    db_location = os.path.join(directory, 'cpu_usage.rrd')
    if txt_backup:
        file_location = os.path.join(directory, 'cpu_usage.txt')
        # Create txt log file
        os.umask(0)
        open(os.open(file_location, os.O_CREAT | os.O_WRONLY, 0o777), 'w+').close()
    # Create round-robin database
    rrdtool.create( db_location, 
                    '--start', 'now', 
                    '--step', str(time_interval), 
                    'DS:user:GAUGE:'+str(time_wait_value)+':0:U',
                    'DS:system:GAUGE:'+str(time_wait_value)+':0:U',
                    'DS:idle:GAUGE:'+str(time_wait_value)+':0:U', 
                    'DS:nice:GAUGE:'+str(time_wait_value)+':0:U', 
                    'RRA:AVERAGE:0.5:1:100')

"""DATA COLLECTION FUNCTIONS"""
def ip_info(snmp_engine, user, upd_targets, directory, txt_backup=False):
    """Collects information about the IP packets going through this agent's interfaces"""
    db_location = os.path.join(directory, 'ip.rrd')
    if txt_backup:
        file_location = os.path.join(directory, 'ip.txt')
    else:
        file_location = None
    data = (
        ObjectType(ObjectIdentity('IP-MIB', 'ipInReceives', 0)), # Total number of received input datagrams (including those received in error)
        ObjectType(ObjectIdentity('IP-MIB', 'ipInDelivers', 0)), # Total number of input datagrams successfully delivered to IP user protocols
        ObjectType(ObjectIdentity('IP-MIB', 'ipForwDatagrams', 0)) # Number of input datagrams for which this entity was not their final IP destination
    )
    i = 0
    msg = ''
    while i < len(upd_targets) and msg != 'DATA_OK':
        msg = update_rrd(snmp_engine, user, upd_targets[i], data, db_location, file_location)
        i += 1
    if msg != 'DATA_OK':
        print('Unable to get snmp data from agent: %s' % msg, file=sys.stderr)

def ram_info(snmp_engine, user, upd_targets, directory, txt_backup=False):
    """Collects information about the RAM of an agent"""
    db_location = os.path.join(directory, 'ram_usage.rrd')
    if txt_backup:
        file_location = os.path.join(directory, 'ram_usage.txt')
    else:
        file_location = None
    data = (
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memAvailReal', 0)),
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'memTotalFree', 0))
    )
    i = 0
    msg = ''
    while i < len(upd_targets) and msg != 'DATA_OK':
        msg = update_rrd(snmp_engine, user, upd_targets[i], data, db_location, file_location)
        i += 1
    if msg != 'DATA_OK':
        print('Unable to get snmp data from agent: %s' % msg, file=sys.stderr)

def cpu_info(snmp_engine, user, upd_targets, directory, txt_backup=False):
    """Collects information about the CPU usage of an agent"""
    db_location = os.path.join(directory, 'cpu_usage.rrd')
    if txt_backup:
        file_location = os.path.join(directory, 'cpu_usage.txt')
    else:
        file_location = None
    data = (
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuRawUser', 0)), # % user CPU time
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuRawSystem', 0)), # % system CPU time
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuRawIdle', 0)), # % idle CPU time
        ObjectType(ObjectIdentity('UCD-SNMP-MIB', 'ssCpuRawNice', 0)) # % nice CPU time
    )
    i = 0
    msg = ''
    while i < len(upd_targets) and msg != 'DATA_OK':
        msg = update_rrd(snmp_engine, user, upd_targets[i], data, db_location, file_location)
        i += 1
    if msg != 'DATA_OK':
        print('Unable to get snmp data from agent: %s' % msg, file=sys.stderr)

