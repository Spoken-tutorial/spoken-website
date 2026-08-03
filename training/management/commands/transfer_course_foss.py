from django.core.management.base import BaseCommand

from training.models import ILWCourse
from training.models import ILWCourseFossLevel
from creation.models import Level


class Command(BaseCommand):
    help = "Migrate training_ilwcourse_foss to ILWCourseFossLevel"

    def handle(self, *args, **kwargs):

        advanced = Level.objects.get(code='C4')

        # This is the auto-generated through model
        ThroughModel = ILWCourse.foss.through

        created = 0

        for row in ThroughModel.objects.all():
            print(row.ilwcourse_id,row.fosscategory_id)

            obj, is_created = ILWCourseFossLevel.objects.get_or_create(
                course_id=row.ilwcourse_id,
                foss_id=row.fosscategory_id,
                defaults={
                    'level': advanced
                }
            )

            if is_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            "Created {} mappings.".format(created)
        ))