import socket
import os
import sys
import json

from os import path
from cpbox.tool import system
from cpbox.tool import net


def fg_mode():
    return '-it' if sys.stdout.isatty() else '-i'


def get_docker_network_gw(name):
    cmd = 'docker network inspect %s' % (name)
    code, ret = system.run_cmd(cmd)
    network_info = json.loads(ret)
    return network_info[0]['IPAM']['Config'][0]['Gateway']


def docker0_ip():
    if system.get_os_name() == 'mac':
        return get_docker_network_gw('bridge')
    else:
        return net.get_ip_address('docker0')


def base_docker_args(container_name, volumes=None, ports=None, envs=None, working_dir=None):
    args = '--name ' + container_name

    if working_dir:
        args += ' -w ' + working_dir

    if volumes:
        if isinstance(volumes, dict):
            args += ' ' + ' '.join(('-v ' + str(from_) + ':' + to_ for from_, to_ in volumes.items()))
        else:
            args += ' ' + ' '.join(('-v ' + item for item in volumes))
    if ports:
        if isinstance(ports, dict):
            args += ' ' + ' '.join(('-p ' + str(from_) + ':' + str(to_) for from_, to_ in ports.items()))
        else:
            args += ' ' + ' '.join(('-p ' + str(item) for item in ports))
    if envs:
        args += ' ' + ' '.join(('-e ' + item for item in envs))

    if path.isfile('/etc/localtime'):
        args += ' -v /etc/localtime:/etc/localtime'

    return args
