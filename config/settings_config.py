import os
import sys
import socket

from django.core.management.utils import get_random_secret_key


def patch_settings():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir_name, '..', 'settings.py')
    if not os.path.exists(path):
        sys.stdout.write('Error not found file settings.py check its availability: project_name/settings.py')
        return sys.exit(1)

    with open(path, 'r') as st_original:
        original = st_original.read()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
    original = original.replace('ALLOWED_HOSTS = [\'*\']', 'ALLOWED_HOSTS = [\'{0}\']'.format(ip))

    with open(path, 'w') as st_new:
        st_new.write(original)


if __name__ == '__main__':
    patch_settings()
