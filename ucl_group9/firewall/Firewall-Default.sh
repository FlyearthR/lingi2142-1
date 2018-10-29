#!/bin/bash

# Flush all rules and chains
# Counters back to zero
ip6tables -F
ip6tables -X
ip6tables -Z

# Default policy
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT DROP

# Allow loopback
ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# Allow established and related connections
ip6tables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Dropping invalid packets
ip6tables -A INPUT -m state --state INVALID -j DROP
ip6tables -A FORWARD -m state --state INVALID -j DROP
ip6tables -A OUTPUT -m state --state INVALID -j DROP
