#! /bin/sh -x

if [[ -f /tmp/podman.sock ]]
then
	rm /tmp/podman.sock
fi

mkdir -pv /dev/shm/build

podman system prune -f

podman ps --all | grep registry
if [[ $? -eq 0 ]]
then
	podman rm -f registry
fi
podman run -it -d -p 5000:5000 --name registry --ip 10.88.0.2 docker.io/registry:2

podman pull docker.io/library/alpine:3.12
podman push docker.io/library/alpine:3.12 localhost:5000/alpine:3.12

# launch podman API
podman system service unix:///tmp/podman.sock --time=0 &

# create gitolite instance, start it and finish setup
docker ps --all | grep gitolite
if [[ $? -eq 0 ]]
then
	docker rm -f gitolite
fi 
docker build -t gitolite -f gitolite/Dockerfile gitolite
docker run -d -v /tmp/podman.sock:/tmp/podman.sock -p 2222:22 --name gitolite gitolite
docker exec -i gitolite chown git /tmp/podman.sock

# create ctl instance
podman ps --all | grep ctl
if [[ $? -eq 0 ]]
then
	podman rm -f ctl
fi
podman build -t ctl -f ctl/Dockerfile ctl/
podman create --device /dev/fuse -v /tmp/podman.sock:/tmp/podman.sock -v /dev/shm/build:/dev/shm/build --name ctl ctl

# open port 
iptables -A CNI-ADMIN -p tcp --dport 5000 -d 10.88.0.2 -j ACCEPT
