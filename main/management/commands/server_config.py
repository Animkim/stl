import os
import sys
import socket

from django.conf import settings
from django.core.management.base import BaseCommand

from stl.main.models import SiteData


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

