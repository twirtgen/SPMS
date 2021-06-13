#! /bin/sh -xe

CONTAINER_RUNTIME="docker"

#echo http://dl-cdn.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories
#apk add podman fuse-overlayfs

# https://github.com/containers/fuse-overlayfs#static-build
#mknod /dev/fuse -m 0666 c 10 229
#cp ctl/registries.conf /etc/containers/

mkdir -pv /dev/shm/build

#${CONTAINER_RUNTIME} create -p 5000:5000 --name registry --ip 10.88.0.2 docker.io/registry:2

if [[ "${CONTAINER_RUNTIME}" != "docker" ]]
then
	# open port
	iptables -A CNI-ADMIN -p tcp --dport 5000 -d 10.88.0.2 -j ACCEPT
	iptables-save > iptables.dump
fi

#${CONTAINER_RUNTIME} pull docker.io/library/alpine:3.12
#podman push docker.io/library/alpine:3.12 localhost:5000/alpine:3.12
#${CONTAINER_RUNTIME} tag docker.io/library/alpine:3.12 localhost:5000/alpine:3.12
#${CONTAINER_RUNTIME} push localhost:5000/alpine:3.12

# launch podman API
#${CONTAINER_RUNTIME} system service unix:///tmp/podman.sock --time=0 &

# create gitolite instance, start it and finish setup
${CONTAINER_RUNTIME} build -t gitolite -f gitolite/Dockerfile gitolite
#podman create -v /tmp/podman.sock:/tmp/podman.sock -p 2222:22 --name gitolite gitolite
${CONTAINER_RUNTIME} create -v /var/run/docker.sock:/var/run/docker.sock -p 2222:22 --name gitolite gitolite
${CONTAINER_RUNTIME} start gitolite
#${CONTAINER_RUNTIME} exec -i gitolite chown git /tmp/podman.sock
${CONTAINER_RUNTIME} exec -i gitolite chown git /var/run/docker.sock

${CONTAINER_RUNTIME} create -p 5000:5000 --name registry docker.io/registry:2
${CONTAINER_RUNTIME} start registry

# create ctl instance
${CONTAINER_RUNTIME} build -t ctl -f ctl/Dockerfile ctl/
#podman create --device /dev/fuse -v /tmp/podman.sock:/tmp/podman.sock -v /dev/shm/build:/dev/shm/build --name ctl ctl
${CONTAINER_RUNTIME} create -v /var/run/docker.sock:/var/run/docker.sock -v /dev/shm/build:/dev/shm/build --name ctl ctl

# otherwise packer build hangs infinitely
#pkill podman
