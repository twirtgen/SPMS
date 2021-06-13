#! /bin/sh -xe

chown git /tmp/admin.pub
passwd -u git
su - git -c "gitolite setup -pk /tmp/admin.pub"
mkdir -pv /mnt/repositories
mv /var/lib/git/repositories/* /mnt/repositories/
chown -R git:git /mnt/repositories
mv /tmp/gitolite.rc /var/lib/git/.gitolite.rc

# Generate SSH host keys
ssh-keygen -A
