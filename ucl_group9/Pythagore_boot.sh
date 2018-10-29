#!/bin/bash

sysctl -p

"`dirname \"$0\"`"/firewall/Firewall.sh Pythagore 300
