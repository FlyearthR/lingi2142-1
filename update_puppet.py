bgp = ['Pythagore', 'Halles']
nodes = ['Carnoy', 'SH1C', 'Stevin', 'Michotte']
monitors = ['MO1', 'MO2']
ns = ['NS1', 'NS2']

pp = 'ucl_group9/%s/puppet/site.pp'
yaml = 'ucl_group9/%s/puppet/data/node.yaml'

data_bgp = """# SNMP specific infos
snmp::sysLocation: %s building
snmp::sysContact: Group 9 <arthur.sluyters@student.uclouvain.be>
snmp::trap_functions: 
  - bgp
  - ospf
snmp::is_monitor: false"""
data_node = """# SNMP specific infos
snmp::sysLocation: %s building
snmp::sysContact: Group 9 <arthur.sluyters@student.uclouvain.be>
snmp::trap_functions: 
  - ospf
snmp::is_monitor: false"""
data_monitor = """---
name: %s
# SNMP specific infos
snmp::sysLocation: %s building
snmp::sysContact: Group 9 <arthur.sluyters@student.uclouvain.be>
snmp::trap_functions:
  - dns
snmp::is_monitor: true"""
data_ns = """---
name: %s
# SNMP specific infos
snmp::sysLocation: %s building
snmp::sysContact: Group 9 <arthur.sluyters@student.uclouvain.be>
snmp::trap_functions: []
snmp::is_monitor: false"""

pp_text = """$default_path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Exec { path => $default_path }
include snmp
"""

def write_data(filename, data):
    with open(filename, 'a') as f:
        f.write(data)

for node in monitors:
    write_data(pp % node, pp_text)
    write_data(yaml % node, data_monitor % (node, node))

for node in ns:
    write_data(pp % node, pp_text)
    write_data(yaml % node, data_ns % (node, node))
