#!/usr/bin/python3
"""Script heavily inspired from http://snmplabs.com/pysnmp/examples/v3arch/asyncore/manager/ntfrcv/snmp-versions.html"""
import os, time
# Imports for snmp traps
from pysnmp.entity import engine, config
from pysnmp.carrier.asyncore.dgram import udp6
from pysnmp.entity.rfc3413 import ntfrcv
from pysnmp.smi import builder, compiler, view, rfc1902

# Port
TRAP_PORT = 162

# Path
TRAP_LOG_PATH = '/etc/monitoring/traps.txt'

def main():
    # Instantiate snmp engine
    snmpEngine = engine.SnmpEngine()

    # Load MIBs (for translation of the numeric OIDs)
    mibBuilder = builder.MibBuilder().loadModules('SNMPv2-MIB', 'SNMP-COMMUNITY-MIB')
    mibViewController = view.MibViewController(mibBuilder)

    # Transport setup
    # UDP over IPv6, listening interface/port
    config.addTransport(
        snmpEngine,
        udp6.domainName + (1,),
        udp6.Udp6Transport().openServerMode(('::', TRAP_PORT))
    )

    # SNMPv2c setup
    # SecurityName <-> CommunityName mapping
    config.addV1System(snmpEngine, 'my-area', 'public')


    # Callback function for receiving notifications
    # noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
    def cbFun(snmpEngine, stateReference, contextEngineId, contextName,
            varBinds, cbCtx):
        # Translate numerical OIDs into human readable form
        varBinds = [rfc1902.ObjectType(rfc1902.ObjectIdentity(x[0]), x[1]).resolveWithMib(mibViewController) for x in varBinds]

        # Turn on write permission for everyone
        os.umask(0)
        # Open file, append new data at the end
        with open(os.open(TRAP_LOG_PATH, os.O_CREAT | os.O_WRONLY, 0o777), 'a+') as f:
            t = time.gmtime()
            f.write('TRAP received on %s from ContextEngineId "%s", ContextName "%s" \n' % (time.strftime('%c', t), contextEngineId.prettyPrint(),
                                                                            contextName.prettyPrint()))
            # Write data in file
            for varbind in varBinds:
                f.write(varbind.prettyPrint()+'\n')
            f.write('\n')
            
    # Register SNMP Application at the SNMP engine
    ntfrcv.NotificationReceiver(snmpEngine, cbFun)

    snmpEngine.transportDispatcher.jobStarted(1)  # Start a job that will never finish

    # Run I/O dispatcher which would receive queries and send confirmations
    try:
        snmpEngine.transportDispatcher.runDispatcher()
    except:
        snmpEngine.transportDispatcher.closeDispatcher()
        raise

main()
