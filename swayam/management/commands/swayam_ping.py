from django.core.management.base import BaseCommand

from swayam.client import SwayamClient


class Command(BaseCommand):
    help = 'Test the SWAYAM Plus API connection.'

    def handle(self, *args, **options):
        client = SwayamClient()

        data = client.ping()

        self.stdout.write(
            self.style.SUCCESS(
                'SWAYAM connection successful.'
            )
        )

        self.stdout.write(
            'Client ID: {}'.format(
                data.get('clientId')
            )
        )

        self.stdout.write(
            'Scopes: {}'.format(
                ', '.join(data.get('scopes', []))
            )
        )