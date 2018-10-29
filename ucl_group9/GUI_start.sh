#!/bin/bash

ip address add dev GUI-eth0 fd00:300:9:5600::1/64

ip -6 route add ::/0 via fd00:300:9:5600:: dev GUI-eth0
