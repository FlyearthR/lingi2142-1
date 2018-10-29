import subprocess
import shlex

with open('ips.txt', 'r') as f:
    lines = f.readlines()
    names = []
    ips = []
    for line in lines:
        name, ip = line.split()
        names.append(name)
        ips.append(ip)

    for name in names:
        print('------------------------ PING6 FROM %s ----------------------' % name)
        for ip in ips:
            p = subprocess.Popen(shlex.split('ip netns exec %s ping6 -c 1 %s' % (name, ip)), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print('[%s] %s' % (name, out.decode('utf-8')))
