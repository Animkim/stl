#!/usr/bin/env python

import os
import sys
import argparse

from django.core.management.utils import get_random_secret_key


def patch_settings():
    if not os.path.exists('../settings.py'):
        sys.stdout.write(
            'Error not found file settings.py'
            'check its availability: {0}'.format('../settings.py')
        )
        return sys.exit(1)

    with open('../settings.py', 'r') as st_original:
        original = st_original.read()

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))

    with open('../settings.py', 'w') as st_new:
        st_new.write(original)


def patch_nginx_config(params):
    if not os.path.exists('nginx.conf'):
        sys.stdout.write(
            'Error not found file nginx.conf'
            'check its availability: {0}'.format('nginx.conf')
        )
        return sys.exit(1)

    with open('nginx.conf', 'r') as nx_original:
        original = nx_original.read()

    original.replace('{server_name}', params.server_name)
    original.replace('{username}', params.username)
    original.replace('{project_name}', params.project_name)

    with open('nginx.conf', 'w') as nx_new:
        nx_new.write(original)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='username', action='store')
    parser.add_argument(dest='server_name', action='store')
    parser.add_argument(dest='project_name', action='store')
    args = parser.parse_args(sys.argv[1:])

    patch_settings()
    patch_nginx_config(args)
