#! /bin/bash

TIMEOUT=180
N=${1}

if [[ ${N} -ge 1 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc00'
	sleep "${TIMEOUT}"
fi

if [[ ${N} -ge 2 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc01'
	sleep "${TIMEOUT}"
fi

if [[ ${N} -ge 4 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc02'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc03'
	sleep "${TIMEOUT}"
fi

if [[ ${N} -ge 8 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc04'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc05'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc06'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc07'
	sleep "${TIMEOUT}"
fi

if [[ ${N} -ge 16 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc08'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc09'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc10'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc11'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc12'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc13'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc14'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc15'
	sleep "${TIMEOUT}"
fi

if [[ ${N} -ge 32 ]]
then
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc16'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc17'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc18'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc19'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc20'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc21'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc22'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc23'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc24'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc25'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc26'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc27'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc28'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc29'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc30'
	mosquitto_pub -h 172.18.0.3 -t '/all' -m 'be.michelfra.disable_cc31'
	sleep "${TIMEOUT}"
fi

echo end
