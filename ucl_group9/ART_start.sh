#!/bin/bash

ip address add dev ART-eth0 fd00:300:9:0300::1/64

ip -6 route add ::/0 via fd00:300:9:0300:: dev ART-eth0
