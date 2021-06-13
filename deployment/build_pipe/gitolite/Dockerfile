FROM alpine:3.12
RUN apk add git gitolite openssh curl
COPY shared/admin.pub /tmp
COPY shared/sshd_config /etc/ssh/sshd_config
COPY shared/bootstrap.sh /tmp
COPY shared/gitolite.rc /tmp
RUN chmod +x /tmp/bootstrap.sh && ./tmp/bootstrap.sh
EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
