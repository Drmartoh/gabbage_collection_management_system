"""
Reset database for development: remove SQLite file and run migrations.
Use when you get InconsistentMigrationHistory (e.g. admin applied before accounts).
"""
import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Reset DB (delete SQLite file) and run migrate. Development only.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_true',
            help='Do not prompt for confirmation.',
        )

    def handle(self, *args, **options):
        db = settings.DATABASES.get('default', {})
        engine = db.get('ENGINE', '')
        name = db.get('NAME', '')

        if 'sqlite' not in engine or not name:
            self.stdout.write(self.style.ERROR('Only SQLite is supported. Your database is: %s' % engine))
            return

        path = name
        if not os.path.isabs(path):
            path = os.path.join(settings.BASE_DIR, path)

        if not options.get('noinput'):
            self.stdout.write('This will delete: %s' % path)
            confirm = input('Type "yes" to continue: ')
            if confirm.lower() != 'yes':
                self.stdout.write('Aborted.')
                return

        if os.path.isfile(path):
            try:
                os.remove(path)
                self.stdout.write(self.style.SUCCESS('Removed %s' % path))
            except OSError as e:
                self.stdout.write(self.style.ERROR('Could not remove file: %s' % e))
                return
        else:
            self.stdout.write('File not found (already clean): %s' % path)

        self.stdout.write('Running migrations...')
        call_command('migrate', '--noinput', verbosity=1)
        self.stdout.write(self.style.SUCCESS('Done. Run seed_gcms and createsuperuser if needed.'))
