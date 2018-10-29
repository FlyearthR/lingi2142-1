#!/bin/bash

# Start of useful adresses
#
PREF200="fd00:200:9"
PREF300="fd00:300:9"

ADM="0000"
STA="1000"
INF="2000"
IOT="3000"
STD="4000"
VST="5000"
# Specific adresses
# Users groups
ADM200="$PREF200:$ADM"
ADM300="$PREF300:$ADM"

STA200="$PREF200:$STA"
STA300="$PREF300:$STA"

INF200="$PREF200:$INF"
INF300="$PREF300:$INF"

IOT200="$PREF200:$IOT"
IOT300="$PREF300:$IOT"

STD200="$PREF200:$STD"
STD300="$PREF300:$STD"

VST200="$PREF200:$VST"
VST300="$PREF300:$VST"

# Machines
DNS1_1="$PREF200:2100::2/128"
DNS1_2="$PREF300:2100::2/128"
DNS2_1="$PREF200:2400::2/128"
DNS2_2="$PREF300:2400::2/128"

MON1_1="$PREF200:2100::1/128"
MON1_2="$PREF300:2100::1/128"
MON2_1="$PREF200:2400::1/128"
MON2_2="$PREF300:2400::1/128"

# End of useful addresses

# OSPF
ip6tables -A INPUT -p 89 -j ACCEPT
ip6tables -A FORWARD -p 89 -j ACCEPT
ip6tables -A OUTPUT -p 89 -j ACCEPT

# DNS
for d in $DNS1_1 $DNS1_2 $DNS2_1 $DNS2_2;
do
	for p in "tcp" "udp";
	do
		ip6tables -A INPUT -s $d -p $p --dport 53 -j ACCEPT
		ip6tables -A FORWARD -s $d -p $p --dport 53 -j ACCEPT
		ip6tables -A FORWARD -d $d -p $p --dport 53 -j ACCEPT
		ip6tables -A OUTPUT -d $d -p $p --dport 53 -j ACCEPT
	done;
done;

## INFRASTRUCTURES ##
for d in "$INF200::/52" "$INF300::/52";
do
	# Allow any infra to host a service
	ip6tables -A INPUT -d $d -j ACCEPT
	ip6tables -A FORWARD -d $d -j ACCEPT
	ip6tables -A OUTPUT -d $d -j ACCEPT

	# Allow any infra to broadcast inside the network
	ip6tables -A INPUT -s $d -j ACCEPT
	ip6tables -A FORWARD -s $d -d "$PREF200::/48" -j ACCEPT
	ip6tables -A FORWARD -s $d -d "$PREF300::/48" -j ACCEPT
	ip6tables -A OUTPUT -s $d -d "$PREF200::/48" -j ACCEPT
	ip6tables -A OUTPUT -s $d -d "$PREF300::/48" -j ACCEPT
done;

## ADMINS ##
for i in "$ADM200::/52" "$ADM300::/52";
do
	ip6tables -A INPUT -s $i -j ACCEPT
	ip6tables -A FORWARD -s $i -j ACCEPT
	ip6tables -A FORWARD -d $i -j ACCEPT
	ip6tables -A OUTPUT -d $i -j ACCEPT
done;

## STAFF ##
for s in "$STA200::/52" "$STA300::/52";
do
	# Allow ssh for the staff (to anywhere)
	ip6tables -A FORWARD -s $s -p tcp --dport 22 -j ACCEPT

	# Allow a staff member to host a service
	ip6tables -A FORWARD -d $s -j ACCEPT
done;

## STUDENTS ##
# Allow ssh for student from inside the network to inside the network
for s in "$STD200::/52" "$STD300::/52";
do
	ip6tables -A FORWARD -s $s -d "$STD200::/52" -p tcp --dport 22 -j ACCEPT
	ip6tables -A FORWARD -s $s -d "$STD300::/52" -p tcp --dport 22 -j ACCEPT
done;

## GLOBAL FOR REGISTERED USERS ##
for i in "$STA200::/52" "$STA300::/52" "$STD200::/52" "$STD300::/52";
do
	ip6tables -A FORWARD -s $i -p tcp -m multiport --dports 53,80,443,5001 -j ACCEPT
	ip6tables -A FORWARD -s $i -p tcp -m multiport --dports 53,80,443,5001 -j ACCEPT
	# ip6tables -A FORWARD -s $i -p udp --dport 53 -j ACCEPT
	# ip6tables -A FORWARD -s $i -p udp --dport 53 -j ACCEPT
done;

## VISITORS ##
# Block traffic toward the outside of the network
for i in "$VST200::/52" "$VST300::/52";
do
	for p in "udp" "tcp";
	do
		ip6tables -A FORWARD -s $i -d "$PREF200::/48" -p $p -m multiport --dports 53,80,443,5001 -j ACCEPT
		ip6tables -A FORWARD -s $i -d "$PREF300::/48" -p $p -m multiport --dports 53,80,443,5001 -j ACCEPT
	done;
	# ip6tables -A FORWARD -s $i -d "$PREF200::/48" -p udp --dport 53 -j ACCEPT
	# ip6tables -A FORWARD -s $i -d "$PREF300::/48" -p udp --dport 53 -j ACCEPT
done;

## IOT ##
# Traffic toward external network blocked in Firewall-InOut.sh
# Allow to send and receive from/to the network
for i in "$IOT200::/52" "$IOT300::/52";
do
	for a in "$PREF200::/48" "$PREF300::/48";
	do
		ip6tables -A INPUT -s $i -d $a -j ACCEPT
		ip6tables -A FORWARD -s $i -d $a -j ACCEPT
		ip6tables -A FORWARD -s $a -d $i -j ACCEPT
		ip6tables -A OUTPUT -s $a -d $i -j ACCEPT
	done;
done;

# Protection against flooding and DoS
ip6tables -A INPUT -p icmpv6 --icmpv6-type 128/0 -m limit --limit 10/minute -j ACCEPT # Echo request
ip6tables -A INPUT -p icmpv6 --icmpv6-type 135/0 -m limit --limit 10/minute -j ACCEPT # Neighbor solicitation
ip6tables -A INPUT -p icmpv6 --icmpv6-type 128/0 -j DROP
ip6tables -A INPUT -p icmpv6 --icmpv6-type 135/0 -j DROP

# Accept other icmpv6 packages
ip6tables -A INPUT -p icmpv6 -j ACCEPT
ip6tables -A FORWARD -p icmpv6 -j ACCEPT
ip6tables -A OUTPUT -p icmpv6 -j ACCEPT

# Record all dropped packets in files
ip6tables -N LOGS
ip6tables -A INPUT -j LOGS
ip6tables -A OUTPUT -j LOGS
ip6tables -A FORWARD -j LOGS
ip6tables -A LOGS -m limit --limit 10/minute -j LOG --log-prefix "IP6Tables-Dropped: " --log-level 4
ip6tables -A LOGS -j DROP
