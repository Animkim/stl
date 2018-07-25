from django.core.management.base import BaseCommand

from stl.main.api import TranioApi


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('command', nargs='+', type=str, help='<ads types places pages meta all>')

    def handle(self, **options):
        methods = options.get('command', ())
        if set(methods) & {'places', 'types'}:
            order_list = ('places', 'types', 'ads')
            methods += ['ads']
            methods = sorted(set(methods), key=lambda m: m in order_list and order_list.index(m) or -1)
        TranioApi().process(methods)

