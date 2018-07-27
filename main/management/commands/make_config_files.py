import os
import re
import sys
import socket

from django.conf import settings
from django.core.management.base import BaseCommand

from stl.main.models import SiteData


def patch_settings(config):
    path = os.path.join(settings.BASE_DIR, 'settings.py')
    if not os.path.exists(path):
        sys.stdout.write('Error not found file settings.py check its availability: {0}}'.format(path))
        return sys.exit(1)

    with open(path, 'r') as settings_old:
        original = settings_old.read()

    original = re.sub(r'ALLOWED_HOSTS = \[.+\]', 'ALLOWED_HOSTS = [\'{0}\']'.format(config.domain), original)
    original = re.sub(r'ACTIVE_LANG = \[.+\]', 'ACTIVE_LANG = [\'{0}\']'.format(config.lang), original)
    original = re.sub(r'DOMAIN = \[.+\]', 'ACTIVE_LANG = [\'{0}\']'.format(config.domain), original)
    with open(path, 'w') as settings_new:
        settings_new.write(original)


def patch_nginx_config(config):
    path = os.path.join(settings.BASE_DIR, 'config', 'nginx_raw.conf')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file nginx.conf check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as nginx_original:
        original = nginx_original.read()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]

    original = original.replace('{host_ip}', ip)
    original = original.replace('{server_name}', config.domain)
    original = original.replace('{username}', config.username)

    with open(os.path.join(os.path.dirname(path), 'nginx.conf'), 'w') as nginx:
        nginx.write(original)


def patch_uwsgi_config(config):
    path = os.path.join(settings.BASE_DIR, 'config', 'uwsgi_raw.ini')
    if not os.path.exists(path):
        sys.stdout.write(
            'Error not found file uwsgi.ini check its availability: {0}'.format(path)
        )
        return sys.exit(1)

    with open(path, 'r') as uwsgi_original:
        original = uwsgi_original.read()

    original = original.replace('{username}', config.username)

    with open(os.path.join(os.path.dirname(path), 'uwsgi.ini'), 'w') as uwsgi:
        uwsgi.write(original)


class Command(BaseCommand):
    def handle(self, **options):
        data = SiteData.objects.last()
        patch_nginx_config(data)
        patch_uwsgi_config(data)
        patch_settings(data)

