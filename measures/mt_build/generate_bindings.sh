#! /bin/bash

PLUGIN_NAME="be.michelfra.disable_cc"

for i in {00..31}
do
	NEW_PLUGIN_NAME="${PLUGIN_NAME}${i}"
	cp -r "${PLUGIN_NAME}" "${NEW_PLUGIN_NAME}"
	mv "${NEW_PLUGIN_NAME}"/disable_cc.plugin "${NEW_PLUGIN_NAME}"/disable_cc"${i}".plugin
	sed -i -e "s/${PLUGIN_NAME}/${NEW_PLUGIN_NAME}/g" "${NEW_PLUGIN_NAME}"/disable_cc"${i}".plugin
	tar -cjf "${NEW_PLUGIN_NAME}.tar.bz2" "${NEW_PLUGIN_NAME}"
	rm -r "${NEW_PLUGIN_NAME}"
	#sha256sum be.michelfra.disable_cc"${i}".tar.bz2
	sshpass -p azerty123  scp "${NEW_PLUGIN_NAME}.tar.bz2" root@10.20.3.50:/root/bindings/"${NEW_PLUGIN_NAME}"
done
