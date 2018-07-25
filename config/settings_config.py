import os
import sys
import socket

from django.core.management.utils import get_random_secret_key


def patch_settings():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(dir_name, '..', 'settings.py')
    if not os.path.exists(settings_path):
        sys.stdout.write('Error not found file settings.py check its availability: {0}}'.format(settings_path))
        return sys.exit(1)

    token_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token')
    if not os.path.exists(token_path):
        sys.stdout.write('Error not found file token check its availability: {0}'.format(token_path))
        sys.exit(1)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    with open(token_path, 'r') as config:
        token = config.read()

    with open(settings_path, 'r') as settings:
        original = settings.read()

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
    original = original.replace('TOKEN_API = \'\'', 'TOKEN_API = \'{0}\''.format(token))
    original = original.replace('ALLOWED_HOSTS = [\'*\']', 'ALLOWED_HOSTS = [\'{0}\']'.format(ip))

    with open(settings_path, 'w') as settings_new:
        settings_new.write(original)


if __name__ == '__main__':
    patch_settings()
