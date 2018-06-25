#!/usr/bin/env python

import os
import sys
import argparse

from django.core.management.utils import get_random_secret_key


def patch_settings(params):
    project = '/home/{0}/stl/'.format(params.username)
    path = os.path.join(project, 'stl', 'settings.py')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file settings.py '
            'check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as st_original:
        original = st_original.read()

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
    # original = original.replace('ALLOWED_HOSTS = []', 'ALLOWED_HOSTS = [\'{0}\']'.format(params.host_ip))
    original = original.replace('ACTIVE_LANG = \'\'', 'ACTIVE_LANG = \'{0}\''.format(params.lang))
    original = original.replace('TOKEN_API = \'\'', 'TOKEN_API = \'{0}\''.format(params.token))

    with open(path, 'w') as st_new:
        st_new.write(original)


def patch_nginx_config(params):
    project = '/home/{0}/stl/'.format(params.username)
    path = os.path.join(project, 'stl/config', 'nginx.conf')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf '
            'check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as nx_original:
        original = nx_original.read()

    original = original.replace('{host_ip}', params.host_ip)
    original = original.replace('{server_name}', params.domain)
    original = original.replace('{username}', params.username)

    with open(path, 'w') as nx_new:
        nx_new.write(original)


def patch_uwsgi_config(params):
    project = '/home/{0}/stl/'.format(params.username)
    path = os.path.join(project, 'stl/config', 'uwsgi.ini')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf '
            'check its availability: uwsgi.ini'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as uw_original:
        original = uw_original.read()

    original = original.replace('{username}', params.username)

    with open(path, 'w') as uw_new:
        uw_new.write(original)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='username', action='store')
    parser.add_argument(dest='domain', action='store')
    parser.add_argument(dest='host_ip', action='store')
    parser.add_argument(dest='token', action='store')
    parser.add_argument(dest='lang', action='store')
    args = parser.parse_args(sys.argv[1:])

    patch_settings(args)
    patch_nginx_config(args)
    patch_uwsgi_config(args)
