#!/bin/bash

apt-get -y -qq --force-yes update
#apt-get -y -qq --force-yes install build-essential checkinstall
#if !which cmake; then
#	wget http://www.cmake.org/files/v3.2/cmake-3.2.2.tar.gz
#	tar xf cmake-3.2.2.tar.gz
#	cd cmake-3.2.2
#	./configure
#	make
#	checkinstall -y
#	cd ..
#fi
#apt-get -y -qq --force-yes update

apt-get -y -qq --force-yes install git bash vim-nox tcpdump nano\
                                          bird6 quagga inotify-tools\
                                          iperf
# dependencies for puppet
# apt-get -y -qq --force-yes install ruby ruby-dev libboost-all-dev gettext curl libcurl4-openssl-dev libyaml-cpp-dev
apt-get -y -qq --force-yes install puppet # TODO Get more recent version of puppet
#gem install puppet -f
apt-get -y -qq --force-yes install nmap # Used for firewall tests

update-rc.d quagga disable &> /dev/null || true
update-rc.d bird disable &> /dev/null || true
update-rc.d bird6 disable &> /dev/null || true

service quagga stop
service bird stop
service bird6 stop

(cd /sbin && ln -s /usr/lib/quagga/* .)

# Install monitoring stuff
sed -i.bak '/http:\/\/httpredir.debian.org\/debian/ s/$/ contrib non-free/' /etc/apt/sources.list # Add contrib non-free to allow installation of snmp-mibs-downloader, create a backup of the file
apt-get update
apt-get -y -qq --force-yes install snmp snmpd snmp-mibs-downloader\
				python3 python3-pip\
				rrdtool python-rrdtool librrd-dev
download-mibs
pip3 install pysnmp
pip3 install pysnmp-mibs
pip3 install rrdtool

systemctl stop snmpd
sudo bash -c "echo 'createUser arthur SHA password AES secret_key' >> /var/lib/snmp/snmpd.conf"
systemctl start snmpd

su vagrant -c 'cd && git clone https://github.com/FlyearthR/lingi2142-1.git'
