from django.core.management.base import BaseCommand

from swayam.services import SwayamEnrollmentService
# schedule this nightly using existing cron infrastructure. SWAYAM explicitly recommends nightly reconciliation.

class Command(BaseCommand):
    help = 'Synchronize SWAYAM Plus enrollments.'

    def handle(self, *args, **options):

        service = SwayamEnrollmentService()

        result = service.sync_all_enrollments()

        self.stdout.write(
            self.style.SUCCESS(
                (
                    'SWAYAM sync finished. '
                    'created={created}, '
                    'updated={updated}, '
                    'failed={failed}'
                ).format(**result)
            )
        )