import os
import sys

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

    with open('../settings.py', 'w') as st_settings:
        st_settings.write(original)
