terraform {
 required_version = ">= 0.13"
  required_providers {
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "0.6.11"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

variable "curdir" {
  type=string
}

resource "libvirt_pool" "SPMS-test" {
  name = "SPMS-test"
  type = "dir"
  path = "${var.curdir}/storage_pools/SPMS-test_storage"
}

resource "libvirt_network" "SPMS_network" {
  # the name used by libvirt
  name = "SPMSnet"

  # mode can be: "nat" (default), "none", "route", "bridge"
  mode = "nat"

  # (optional) the network device for forward
  # should be the network device or bridge. prevents talk between nat networks
  # dev = "eth0"

  #  the domain used by the DNS server in this network
  domain = "SPMS.local"

  #  list of subnets the addresses allowed for domains connected
  # also derived to define the host addresses
  # also derived to define the addresses served by the DHCP server
  #addresses = ["10.20.3.0/24", "2001:db8:ca2:2::1/64"]
  addresses = ["10.20.3.0/24"]

  dns {
	enabled = true
	local_only = true
  }
 }

# Base image root password
variable "root_pass" {
  type=string
}

variable "admin_key_pass" {
  type=string
}

variable "ctl_key_pass" {
  type=string
}

resource "null_resource" "base_layer-build" {
  provisioner "local-exec" {
    command=<<EOF
#! /bin/bash

cd base_layer
if [[ ! -d /tmp/spms/imgs/base_layer ]]
then
  packer build -var root_pass=${var.root_pass} build.json
fi
cd ..
    EOF
  }
}

resource "libvirt_volume" "base-image" {
  name   = "base-image"
  pool = libvirt_pool.SPMS-test.name
  source = "/tmp/spms/imgs/base_layer/base_layer.qcow2"
  depends_on = [null_resource.base_layer-build]
}

resource "null_resource" "build_pipe-build" {
  depends_on = [null_resource.base_layer-build]
  provisioner "local-exec" {
    command=<<EOF
#! /bin/bash

cd build_pipe
if [[ ! -d /tmp/spms/imgs/build_pipe ]]
then
  #ssh-keygen -N ${var.admin_key_pass} -f keys/admin
  #ssh-keygen -N ${var.ctl_key_pass} -f keys/ctl
  ssh-keygen -N '' -f keys/admin
  ssh-keygen -N '' -f keys/ctl
  cp keys/ctl ctl
  cp keys/admin.pub gitolite/shared
  packer build -var root_pass=${var.root_pass} build.json
fi
cd ..
    EOF
  }
}

resource "libvirt_volume" "builder-disk" {
  name   = "builder-disk"
  pool = libvirt_pool.SPMS-test.name
  source = "/tmp/spms/imgs/build_pipe/build_pipe.qcow2"
  depends_on = [null_resource.build_pipe-build]
}

resource "libvirt_domain" "spms-build_pipe-domain" {
  name   = "spms-build_pipe-domain"
  memory = "4096"
  vcpu   = 4

  network_interface {
    network_id = libvirt_network.SPMS_network.id
    addresses = ["10.20.3.5"]
    hostname = "spms-build_pipe-domain"
  }

  boot_device {
    dev = ["hd"]
  }

  disk {
    volume_id = libvirt_volume.builder-disk.id
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
  }

  # Init the build pipe's µservices
  provisioner "remote-exec" {
      inline=[
        "#podman system service unix:///tmp/podman.sock --time=0 &",
        "mkdir /dev/shm/build",
        "#podman start registry",
        "docker start gitolite",
        "docker start registry",
        "#iptables-restore < iptables.dump",
        "sleep 10"
      ]
      connection {
        user="root"
        password="${var.root_pass}"
        host="10.20.3.5"
      }
  }

  # Trigger SPMS's µservices build in the build pipe
  provisioner "local-exec" {
    command=<<EOF
#! /bin/bash -e

# Configure gitolite by adding ctl key and SPMS repo
GIT_SSH_COMMAND="ssh -F ssh_config" git clone gitolite-admin:gitolite-admin
if [[ $? -eq 0 ]]
then
  cp build_pipe/keys/ctl.pub gitolite-admin/keydir
  cp gitolite-admin-data/gitolite.conf gitolite-admin/conf
  cp -r gitolite-admin-data/local gitolite-admin
  git -C gitolite-admin add .
  git -C gitolite-admin commit -m "tmp"
  GIT_SSH_COMMAND="ssh -F ../ssh_config" git -C gitolite-admin push origin -f
  git remote | grep gitolite > /dev/null
  if [[ $? -eq 1 ]]
  then
    git remote add gitolite gitolite-admin:SPMS
    GIT_SSH_COMMAND="ssh -F deployment/ssh_config" git push --set-upstream gitolite main
  else
    GIT_SSH_COMMAND="ssh -F deployment/ssh_config" git push gitolite -f
  fi
fi
  EOF
  }
}

variable "root_ca_pass" {
  type=string
}

variable "pr_pass" {
  type=string
}

variable "pv1_pass" {
  type=string
}

resource "null_resource" "certificates" {
  provisioner "local-exec" {
    command=<<EOF
cd certificates
ROOT_CA_PASS=${var.root_ca_pass} PR_PASS=${var.pr_pass} PR_IP="10.20.3.50" PV1_PASS=${var.pv1_pass} PV1_IP="10.20.3.100" ./generate_certificates.sh
cd ..
    EOF
  }
}

resource "null_resource" "pr-build" {
  depends_on = [libvirt_domain.spms-build_pipe-domain, null_resource.certificates]
  provisioner "local-exec" {
    command=<<EOF
      #! /bin/bash

      if [[ ! -d /tmp/spms/imgs/pr ]]
      then
        while
          CONTAINERS=$(curl 10.20.3.5:5000/v2/_catalog -s | jq -r '.repositories |@sh' | wc -w)
          [[ $CONTAINERS -lt 8 ]] || break
            sleep 20
        do true; done
        cd pr/packer
        packer build -var root_pass=${var.root_pass} -var hostname=pr build.json
      fi
    EOF
  }
}

resource "libvirt_volume" "pr-image" {
  name   = "pr-image"
  pool = libvirt_pool.SPMS-test.name
  source = "/tmp/spms/imgs/pr/pr.qcow2"
  depends_on = [null_resource.pr-build]
}

resource "libvirt_volume" "pr-disk" {
  name = "pr-disk"
  pool = libvirt_pool.SPMS-test.name
  base_volume_id = libvirt_volume.pr-image.id
}

resource "libvirt_domain" "spms-pr-domain" {
  name   = "spms-pr-domain"
  memory = "1024"
  vcpu   = 2

  network_interface {
	network_id = libvirt_network.SPMS_network.id
	addresses = ["10.20.3.50"]
  hostname = "pr-domain"
  wait_for_lease = true
  }

  boot_device {
    dev = ["hd"]
  }

  disk {
    volume_id = libvirt_volume.pr-disk.id
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
  }

  provisioner "remote-exec" {
    inline=[
      "openssl rsa -passin pass:${var.pr_pass} -in pr.key -out /tmp/pr.key",
      "docker stack up -c docker-compose.yml stack"
    ]
    connection {
      user="root"
      password="${var.root_pass}"
      host="10.20.3.50"
    }
  }
}

resource "null_resource" "pv1-build" {
  depends_on = [libvirt_domain.spms-build_pipe-domain]
  provisioner "local-exec" {
    command=<<EOF
	#! /bin/bash
        cd pv/packer
        packer build -var root_pass=${var.root_pass} -var hostname=pv1 -var registry=10.20.3.5:5000 build.json
      fi
    EOF
  }
}

resource "libvirt_volume" "pv1-disk" {
  name = "pv1-disk"
  pool = libvirt_pool.SPMS-test.name
  source = "/tmp/spms/imgs/pv1/pv1.qcow2"
  depends_on = [null_resource.pv1-build]
}

resource "libvirt_domain" "spms-pv1-domain" {
  depends_on = [libvirt_domain.spms-pr-domain]

  name   = "spms-pv1-domain"
  memory = "1024"
  vcpu   = 2

  network_interface {
	  network_id = libvirt_network.SPMS_network.id
	  addresses = ["10.20.3.100"]
	  hostname = "pv1-domain"
  }

  boot_device {
    dev = ["hd"]
  }

  disk {
    volume_id = libvirt_volume.pv1-disk.id
  }

  graphics {
    type        = "vnc"
    listen_type = "address"
  }

 provisioner "remote-exec" {
    inline=[
      "openssl rsa -passin pass:${var.pv1_pass} -in pv.key -out /dev/shm/pv.key",
      "docker stack up -c docker-compose.yml stack"
    ]
    connection {
      user="root"
      password="${var.root_pass}"
      host="10.20.3.100"
    }
  }
}

