#!/usr/bin/env python

import os
import sys
import json

from argparse import Namespace
from django.core.management.utils import get_random_secret_key


def patch_settings():
    project = '/home/{0}/stl/'.format(config.username)
    path = os.path.join(project, 'stl', 'settings.py')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file settings.py check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as st_original:
        original = st_original.read()

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
    # original = original.replace('ALLOWED_HOSTS = []', 'ALLOWED_HOSTS = [\'{0}\']'.format(params.host_ip))
    original = original.replace('ACTIVE_LANG = \'\'', 'ACTIVE_LANG = \'{0}\''.format(config.lang))
    original = original.replace('TOKEN_API = \'\'', 'TOKEN_API = \'{0}\''.format(config.token))
    original = original.replace('DOMAIN = \'\'', 'DOMAIN = \'{0}\''.format(config.domain))
    original = original.replace('LOCATION_PATH = \'\'', 'LOCATION_PATH = \'{0}\''.format(config.location_path))
    original = original.replace('AD_PATH = \'\'', 'AD_PATH = \'{0}\''.format(config.ad_path))

    with open(path, 'w') as st_new:
        st_new.write(original)


def patch_nginx_config():
    project = '/home/{0}/stl/'.format(config.username)
    path = os.path.join(project, 'stl/config', 'nginx.conf')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as nx_original:
        original = nx_original.read()

    original = original.replace('{host_ip}', config.host_ip)
    original = original.replace('{server_name}', config.domain)
    original = original.replace('{username}', config.username)

    with open(path, 'w') as nx_new:
        nx_new.write(original)


def patch_uwsgi_config():
    project = '/home/{0}/stl/'.format(config.username)
    path = os.path.join(project, 'stl/config', 'uwsgi.ini')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as uw_original:
        original = uw_original.read()

    original = original.replace('{username}', config.username)

    with open(path, 'w') as uw_new:
        uw_new.write(original)


if __name__ == '__main__':
    if not os.path.exists('stl/config/stl_config.json'):
        sys.stdout.write(
            'Error not found file nginx.conf check its availability: stl/config/stl_config.json'
        )
        sys.exit(1)

    with open('stl/config/stl_config.json', 'r') as config:
        config = config.read()

    config = json.loads(config)
    config = Namespace(**config)

    patch_settings()
    patch_nginx_config()
    patch_uwsgi_config()
