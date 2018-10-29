"""Launch networking tests
start_tests.py [node] [test]
[node] is a node name (Pythagore, ...)
[test] can be BGP, OSPF
"""
import sys
import os

#TOPO_FILE = 'ucl_topo'
CONFIG_DIR = 'ucl_group9'

def test_bgp(node):
    print('test_bgp')



def test_ospf(node):
    os.system('sudo ip netns exec ' + node + ' ping6 -c 1 2001:4860:4860::8888')

def test_notfound(node):
    print('test_not_found')

cmds = {'BGP':test_bgp, 'OSPF':test_ospf}


node = sys.argv[1]
for arg in sys.argv[2:]:
    cmd = cmds.get(arg, test_notfound)
    cmd(node)



