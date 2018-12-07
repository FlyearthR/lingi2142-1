#!/bin/bash

# First argument should be either 200 or 300
# Name of the interface
interface=""
if [ $1 -eq 200 ]; then
	interface="belnetb"
elif [ $1 -eq 300 ]; then
	interface="belneta"
fi
printf "\$1 = $1\t interface = $interface\n"

# Ips allowed trough this router
router="fd00:$1:9::/48"

IOT1="fd00:200:9:3000::/52"
IOT2="fd00:300:9:3000::/52"

# Dropping packet trying to cross the wrong gate to/from internet
# ip6tables -A INPUT -i $interface ! -d $router -j DROP
# ip6tables -A FORWARD -i $interface ! -d $router -j DROP
# ip6tables -A FORWARD -o $interface ! -s $router -j DROP
# ip6tables -A OUTPUT -o $interface ! -s $router -j DROP

# Dropping inner addresses from outside the network
ip6tables -A INPUT	-i $interface	-s $router	-j DROP
ip6tables -A FORWARD	-i $interface	-s $router	-j DROP

# Allow BGP
for p in "tcp" "udp";
do
	ip6tables -A INPUT	-i $interface	-p $p --dport 179	-j ACCEPT
	ip6tables -A INPUT	-i $interface	-p $p --sport 179	-j ACCEPT
	ip6tables -A OUTPUT	-o $interface	-p $p --dport 179	-j ACCEPT
done;

# Block OSPF
ip6tables -A INPUT	-i $interface	-p 89	-j DROP
ip6tables -A FORWARD	-i $interface	-p 89	-j DROP
ip6tables -A FORWARD	-o $interface	-p 89	-j DROP
ip6tables -A OUTPUT	-o $interface	-p 89	-j DROP

# Bloc IOT
for d in $IOT1 $IOT2;
do
	ip6tables -A FORWARD	-i $interface	-d $d	-j DROP
	ip6tables -A FORWARD	-o $interface	-s $d	-j DROP
done;
