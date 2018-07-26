import os
import sys
import json

from django.core.management.utils import get_random_secret_key


def patch_settings():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(dir_name, '..', 'settings.py')
    if not os.path.exists(settings_path):
        sys.stdout.write('Error not found file settings.py check its availability: {0}}'.format(settings_path))
        return sys.exit(1)

    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'install_config.json')
    if not os.path.exists(config_path):
        sys.stdout.write('Error not found file token check its availability: {0}'.format(config_path))
        sys.exit(1)

    with open(config_path, 'r') as config:
        config = json.load(config.read())
    with open(settings_path, 'r') as settings:
        original = settings.read()

    original = original.replace('SECRET_KEY = \'\'', 'SECRET_KEY = \'{0}\''.format(get_random_secret_key()))
    original = original.replace('TOKEN_API = \'\'', 'TOKEN_API = \'{0}\''.format(config.get('token')))
    original = original.replace('URL_API = \'\'', 'URL_API = \'{0}\''.format(config.get('url_api')))

    with open(settings_path, 'w') as settings_new:
        settings_new.write(original)


if __name__ == '__main__':
    patch_settings()
