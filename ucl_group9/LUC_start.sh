#!/bin/bash

ip address add dev LUC-eth0 fd00:300:9:f::1/64

ip -6 route add ::/0 via fd00:300:9:f:: dev LUC-eth0
