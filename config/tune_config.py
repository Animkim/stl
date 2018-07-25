#!/usr/bin/env python

import os
import sys
import socket

from stl.main.models import SiteData


def patch_nginx_config():
    project = '/home/{0}/stl/'.format(data.username)
    path = os.path.join(project, 'stl/config', 'nginx.conf')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as nx_original:
        original = nx_original.read()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    original = original.replace('{host_ip}', ip)
    original = original.replace('{server_name}', data.domain)
    original = original.replace('{username}', data.username)

    with open(path, 'w') as nx_new:
        nx_new.write(original)


def patch_uwsgi_config():
    project = '/home/{0}/stl/'.format(data.username)
    path = os.path.join(project, 'stl/config', 'uwsgi.ini')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file uwsgi.ini check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as uw_original:
        original = uw_original.read()

    original = original.replace('{username}', data.username)

    with open(path, 'w') as uw_new:
        uw_new.write(original)


if __name__ == '__main__':
    data = SiteData.objects.last()
    if not data:
        sys.stdout.write('Error not found model SiteData')
        sys.exit(1)

    patch_nginx_config()
    patch_uwsgi_config()
