FROM alpine:3.12

#RUN #echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories &&\
	#echo http://dl-cdn.alpinelinux.org/alpine/edge/community >> /etc/apk/repositories &&\
#	apk update &&\
	#apk add curl openssh python3 py3-pip git make coreutils buildah runc tzdata
#	apk add curl openssh python3 py3-pip git make coreutils

RUN apk update &&\
	apk add curl openssh python3 py3-pip git make coreutils

RUN pip3 install jinja2 &&\
	ssh-keygen -A && \
	mkdir -pv ~/.ssh/ &&\
	ssh-keyscan -t rsa 172.17.0.2 >> ~/.ssh/known_hosts

COPY ctl .
COPY config /root/.ssh/config
RUN chmod 600 ctl

#COPY registries.conf /etc/containers/
#COPY policy.json /etc/containers/
#RUN sed -i -e 's/^\#mount_program/mount_program/g' /etc/containers/storage.conf

#ENV BUILDAH_ISOLATION=chroot
#ENV REGISTRY=10.88.0.2:5000
ENV REGISTRY=localhost:5000
#ENV BUILDER=buildah
ENV BUILDER=docker
ENV BRANCH=main

COPY script.sh .
#VOLUME /tmp/podman.sock
CMD ./script.sh
