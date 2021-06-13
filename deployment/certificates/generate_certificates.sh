#! /bin/sh -e

export ROOT_CA="root_ca"
ROOT_CA_PASS="${ROOT_CA_PASS}"

NAME="${ROOT_CA}" PASS="${ROOT_CA_PASS}" ./generate_ca.sh
NAME="pr" PASS="${PR_PASS}" IP="${PR_IP}" ./generate_host.sh
NAME="pv1" PASS="${PV1_PASS}" IP="${PV1_IP}" ./generate_host.sh
