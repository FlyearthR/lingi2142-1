#!/bin/bash

ip netns exec "Carnoy" "`dirname \"$0\"`"/firewall/Firewall.sh Carnoy

ip netns exec "Stevin" "`dirname \"$0\"`"/firewall/Firewall.sh Stevin

ip netns exec "Halles" "`dirname \"$0\"`"/firewall/Firewall.sh Halles 200

ip netns exec "Pythagore" "`dirname \"$0\"`"/firewall/Firewall.sh Pythagore 300

ip netns exec "SH1C" "`dirname \"$0\"`"/firewall/Firewall.sh SH1C

ip netns exec "Michotte" "`dirname \"$0\"`"/firewall/Firewall.sh Michotte
