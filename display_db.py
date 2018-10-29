import os
import sys
import tempfile
import rrdtool 

CFG_FILE_PATH = 'ucl_group9/SH1C/scripts/agent_list.conf'
SNMP_LOG_PATH = 'ucl_group9/SH1C/monitoring'

GRAPH_START = '-1000'
GRAPH_END = 'now'

def graph_ram_info(db_directory):
    db_location = os.path.join(db_directory, 'ram_usage.rrd')
    img_location = os.path.join(db_directory, 'ram_usage.png')
    rrdtool.graph(  img_location,
                    '--width', '1080',
                    '--height', '300',
                    '--start', GRAPH_START,
                    '--end', GRAPH_END,
                    '--vertical-label', 'MB',
                    '--title', 'Used/free RAM',
                    '--lower-limit', '0',
                    'DEF:used_ram='+db_location+':used:AVERAGE',
                    'DEF:free_ram='+db_location+':free:AVERAGE',
                    'LINE1:free_ram#00FF00:Free RAM',
                    'LINE1:used_ram#FF0000:Used RAM ',
                    )

def graph_cpu_info(db_directory):
    db_location = os.path.join(db_directory, 'cpu_usage.rrd')
    img_location = os.path.join(db_directory, 'cpu_usage.png')
    rrdtool.graph(  img_location,
                    '--width', '1080',
                    '--height', '300',
                    '--start', GRAPH_START,
                    '--end', GRAPH_END,
                    '--vertical-label', '%',
                    '--title', 'CPU usage',
                    '--lower-limit', '0',
                    '--upper-limit', '100',
                    'DEF:cpu_user='+db_location+':user:AVERAGE',
                    'DEF:cpu_system='+db_location+':system:AVERAGE',
                    'DEF:cpu_idle='+db_location+':idle:AVERAGE',
                    'DEF:cpu_nice='+db_location+':nice:AVERAGE',
                    'CDEF:p_cpu_user=100,cpu_user,cpu_user,cpu_system,+,cpu_idle,+,cpu_nice,+,/,*',
                    'CDEF:p_cpu_system=100,cpu_system,cpu_user,cpu_system,+,cpu_idle,+,cpu_nice,+,/,*',
                    'CDEF:p_cpu_idle=100,cpu_idle,cpu_user,cpu_system,+,cpu_idle,+,cpu_nice,+,/,*',
                    'CDEF:p_cpu_nice=100,cpu_nice,cpu_user,cpu_system,+,cpu_idle,+,cpu_nice,+,/,*',
                    'LINE1:p_cpu_user#00FF00:User CPU percentage',
                    'LINE1:p_cpu_system#FF0000:System CPU percentage',
                    'LINE1:p_cpu_idle#070070:Idle CPU percentage',
                    'LINE1:p_cpu_nice#0000FF:Nice CPU percentage',
                    )
                    
def graph_ip_info(db_directory):
    db_location = os.path.join(db_directory, 'ip.rrd')
    img_location = os.path.join(db_directory, 'ip.png')
    rrdtool.graph(  img_location,
                    '--width', '1080',
                    '--height', '300',
                    '--start', GRAPH_START,
                    '--end', GRAPH_END,
                    '--vertical-label', 'datagrams/s',
                    '--title', 'IP',
                    '--lower-limit', '0',
                    'DEF:ip_received='+db_location+':received:AVERAGE',
                    'DEF:ip_delivered='+db_location+':delivered:AVERAGE',
                    'DEF:ip_forwarded='+db_location+':forwarded:AVERAGE',
                    'LINE1:ip_received#00FF00:Total',
                    'LINE1:ip_delivered#FF0000:Delivered',
                    'LINE1:ip_forwarded#070070:Forwarded',
                    )

def graph_udp_info(db_directory):
    db_location = os.path.join(db_directory, 'udp.rrd')
    img_location = os.path.join(db_directory, 'udp.png')
    rrdtool.graph(  img_location,
                    '--width', '1080',
                    '--height', '300',
                    '--start', GRAPH_START,
                    '--end', GRAPH_END,
                    '--vertical-label', 'datagrams/s',
                    '--title', 'UDP',
                    '--lower-limit', '0',
                    'DEF:udp_delivered='+db_location+':delivered:AVERAGE',
                    'DEF:udp_sent='+db_location+':sent:AVERAGE',
                    'DEF:udp_notdelivered_noport='+db_location+':notdelivered_noport:AVERAGE',
                    'DEF:udp_notdelivered_error='+db_location+':notdelivered_error:AVERAGE',
                    'LINE1:udp_delivered#00FF00:Delivered',
                    'LINE1:udp_sent#FF0000:Sent',
                    'LINE1:udp_notdelivered_noport#070070:Not delivered (no port)',
                    'LINE1:udp_notdelivered_error#0000FF:Not delivered (other errors)',
                    )

def graph_tcp_info(db_directory):
    db_location = os.path.join(db_directory, 'tcp.rrd')
    img_location = os.path.join(db_directory, 'tcp.png')
    rrdtool.graph(  img_location,
                    '--width', '1080',
                    '--height', '300',
                    '--start', GRAPH_START,
                    '--end', GRAPH_END,
                    '--vertical-label', 'segments/s',
                    '--title', 'TCP',
                    '--lower-limit', '0',
                    'DEF:tcp_received_total='+db_location+':received_total:AVERAGE',
                    'DEF:tcp_received_error='+db_location+':received_error:AVERAGE',
                    'DEF:tcp_sent='+db_location+':sent:AVERAGE',
                    'DEF:tcp_retransmitted='+db_location+':retransmitted:AVERAGE',
                    'LINE1:tcp_received_total#00FF00:Received (total)',
                    'LINE1:tcp_received_error#FF0000:Received (error)',
                    'LINE1:tcp_sent#070070:Sent',
                    'LINE1:tcp_retransmitted#0000FF:Retransmitted',
                    )



with open(CFG_FILE_PATH, 'r') as f:
    for line in f:
        agent_name = line.split()[0]
        db_directory = os.path.join(SNMP_LOG_PATH, agent_name)
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)
        graph_ip_info(db_directory)
