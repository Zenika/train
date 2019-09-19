#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


import requests


# helper functions
def check_url(path, version):
    """Check for valid URL"""
    print 'Checking URL: https://{0}/docker-{1}'.format(path, version)
    return 'https://{0}/docker-{1}'.format(path, version)


def get_txt(path, version):
    """Custom Docker install text"""
    txt = 'curl -sSL https://get.docker.com/ | sh\n'.format(path) + \
          'mv /usr/bin/docker /usr/bin/docker.org\n' + \
          'wget https://{0}/docker-{1} -O /usr/bin/docker\n'.format(path, version) + \
          'chmod +x /usr/bin/docker\n'
    return txt


def get_custom(prompt):
    """Prompt for custom Docker version"""

    version = raw_input(prompt)
    if 'rc' in version:
        path = 'test.docker.com/builds/Linux/x86_64'
    elif 'dev' in version:
        path = 'master.dockerproject.org/linux/amd64'
    else:
        path = 'get.docker.com/builds/Linux/x86_64'

    r = requests.head(check_url(path, version))
    if r.status_code != 200:
        print 'Unable to locate specified version.'
        txt = get_custom('\nEnter a different version: ')
    else:
        txt = get_txt(path, version)

    return txt

kube_version="1.16"

# prompts
os.system('clear')

txt = "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -\n" + \
    'echo "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable" | tee /etc/apt/sources.list.d/docker.list\n' + \
    'apt-get update && apt-get install -y docker-ce\n'


# instance configs
PRIMARY_OS = 'Ubuntu-18.04'
PRIMARY = '''#!/bin/sh

FQDN="{{fqdn}}"

export DEBIAN_FRONTEND=noninteractive

# locale
locale-gen en_US.UTF-8

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

# updates
apt-get update && apt-get install -y \
    apt-transport-https \
    git \
    jq \
    linux-image-extra-$(uname -r) \
    linux-image-extra-virtual \
    python \
    tree

# docker
{0}

systemctl start docker
sleep 15

usermod -aG docker ubuntu

# kube*
apt-get update && apt-get install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get update
apt-get install -y kubelet={1}* kubeadm={1}* kubectl={1}*
apt-mark hold kubelet kubeadm kubectl

{{dinfo}}
reboot
'''.format(txt, kube_version)

# Script to use if launching from a custom lab AMI image
AMIBUILD = '''#!/bin/sh
#
FQDN="{{fqdn}}"

# hostname
hostnamectl set-hostname $FQDN
sed -i "1 c\\127.0.0.1 $FQDN localhost" /etc/hosts

{{dinfo}}
reboot
'''.format()


def pre_process():
    """Executed before launching instances in AWS"""
    pass

def post_process():
    """Executed after launching instances in AWS"""
    pass
