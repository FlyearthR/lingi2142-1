#!/bin/bash

ip address add dev SH2-eth0 fd00:300:9:1200::2/64

ip -6 route add ::/0 via fd00:300:9:1200:: dev SH2-eth0

