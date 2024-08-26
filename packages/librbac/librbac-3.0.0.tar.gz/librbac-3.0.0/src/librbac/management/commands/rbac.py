from django.core.management.base import BaseCommand

from librbac import rbac


class Command(BaseCommand):

    """Management команда для работы с разрешениями RBAC."""

    def add_arguments(self, parser):
        parser.add_argument(
            '--list-permissions', action='store_true', help='Напечатать список загруженных разрешений'
        )
        parser.add_argument(
            '--publish-permissions', action='store_true', help='Сохранить загруженные разрешения в хранилище'
        )

    def _value_to_str(self, value) -> str:
        return str(value) if value else '-'

    def _write_table(self, data: list, headers=None):

        if headers:
            data.insert(0, headers)

        col_widths = tuple(max(len(self._value_to_str(item)) for item in col) for col in zip(*data))

        separator = '-+-'.join('-' * width for width in col_widths)

        for num, row in enumerate(data):
            self.stdout.write(" | ".join(self._value_to_str(item).ljust(width) for item, width in zip(row, col_widths)))
            if num == 0 and headers:
                self.stdout.write(separator)

    def handle(self, *args, **options):

        if options['list_permissions']:
            header = ('namespace', 'resource', 'action', 'scope', 'title')
            data = []
            for permission, _ in rbac.permissions.graph:
                title = rbac.permissions.metadata_mapping[permission].title
                data.append((permission.namespace, permission.resource, permission.action, permission.scope, title))
            self._write_table(data, header)

        if options['publish_permissions']:
            self.stdout.write('Сохранение собранных из системы разрешений в хранилище...')
            rbac.publish_permissions()
            self.stdout.write('Завершено.')
