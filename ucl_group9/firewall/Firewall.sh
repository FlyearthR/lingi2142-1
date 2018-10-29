#!/bin/bash

# $1	: Router name
# $2	: 200/300/-

MY_PATH="`dirname \"$0\"`"

printf "[Firewall] [$1] Setting up...\n"
$MY_PATH/Firewall-Default.sh
if [ $# -gt 1 ] ; then
	printf "[Firewall] [$1] Firewall-InOut $2\n"
	$MY_PATH/Firewall-InOut.sh $2
fi
$MY_PATH/Firewall-SetUp.sh
printf "[Firewall] [$1] Done!\n"
