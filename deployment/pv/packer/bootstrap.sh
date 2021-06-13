#! /bin/bash -x

REGISTRY=10.20.3.5:5000
# TODO : avoid hard-coding those values
SERVICES=( "binding_manager_service" "mt_manager_service" "pr_gateway_service" "user_gateway_service" "logger_service" "stack_render_layer")

pull_and_rename () {
	local image="${1}"
	local reg="${REGISTRY}/${image}"
	docker pull "${reg}"
	docker tag "${reg}" "${image}"
}

# Apply new daemon.json config
rc-service docker restart && sleep 2

IMAGES=( $(curl "${REGISTRY}/v2/_catalog" -s | jq -r '.repositories | @sh' | tr -d \'\") )
for i in "${SERVICES[@]}"
do
	echo  "${IMAGES[@]}" | grep -q -w "${i}" 
	if [[ $? -eq 0 ]]
	then
		pull_and_rename "${i}"
	fi
done

VERIFIERS=($(cat /root/pv.config | jq -r '.verifiers | flatten | map(.verifier) | unique | @sh' | tr -d \'\"))
for i in "${VERIFIERS[@]}"
do
	VERIFIER="${i}_verifier"
	echo  "${IMAGES[@]}" | grep -q -w "${VERIFIER}" 
	if [[ $? -eq 0 ]]
	then
		pull_and_rename "${VERIFIER}"
	fi
done

docker run -v $(pwd):/output -v $(pwd)/pv.config:/tmp/stack.config stack_render_layer
docker swarm init
