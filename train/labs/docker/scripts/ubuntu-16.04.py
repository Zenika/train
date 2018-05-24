#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re


import requests


# helper functions
def parse_version(version):
    """Parse and normalize version"""
    m = re.match(r'\d{2}\.\d{2}\.\d+(?:-ce)?(?:-(?:beta|rc)\d+)?', version)
    if m:
        return version
    print 'Unable to parse specified version (format=XX.YY.Z[-ce][-(beta|rc)N]).'
    return None


def check_url(path, version):
    """Check for valid URL"""
    print 'Checking URL: https://{0}/docker-{1}.tgz'.format(path, version)
    return 'https://{0}/docker-{1}.tgz'.format(path, version)


def get_txt(version, channel):
    """Custom Docker install text"""
    txt = 'export VERSION={0} CHANNEL={1} && curl -sSL https://get.docker.com/ | sh\n'.format(version, channel)
    return txt


def get_custom(prompt):
    """Prompt for custom Docker version"""

    version = None
    while not version:
        version = parse_version(raw_input(prompt))
        prompt = '\nEnter a different version: '

    channel = 'test'
    path = 'download.docker.com/linux/static/{0}/x86_64'.format(channel)
    r = requests.head(check_url(path, version))
    if r.status_code != 200:
        print 'Unable to locate specified version.'
        txt = get_custom('\nEnter a different version: ')
    else:
        txt = get_txt(version, channel)

    return txt


# prompts
os.system('clear')
docker = raw_input("""
Which version of Docker do you want to install?

  - stable [default]
  - rc (test)
  - experimental (nightly)
  - edge [deprecated]
  - custom

Enter version (Press enter for default): """)

# example urls
#https://download.docker.com/linux/static/nightly/x86_64/docker-18.06.0-ce-dev.tgz
#https://download.docker.com/linux/static/test/x86_64/docker-18.05.0-ce-rc1.tgz
#https://download.docker.com/linux/static/edge/x86_64/docker-18.05.0-ce.tgz

docker = docker.lower()
if docker == '' or docker == 'stable':
    txt = 'curl -sSL https://get.docker.com/ | sh'
elif docker == 'rc':
    txt = 'export CHANNEL=test && curl -sSL https://get.docker.com/ | sh'
elif docker == 'experimental':
    txt = 'export CHANNEL=nightly && curl -sSL https://get.docker.com/ | sh'
elif docker =='edge':
    txt = 'export CHANNEL=edge && curl -sSL https://get.docker.com/ | sh'
elif docker == 'custom':
    txt = get_custom('Enter version: ')
else:
    print "ERROR: Not a valid option."
    sys.exit()


# instance configs
PRIMARY_OS = 'Ubuntu-16.04'
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
    tree

# docker
{0}

systemctl start docker
sleep 15

usermod -aG docker ubuntu

# compose
curl -L https://github.com/docker/compose/releases/download/1.11.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

{{dinfo}}
reboot
'''.format(txt)

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
