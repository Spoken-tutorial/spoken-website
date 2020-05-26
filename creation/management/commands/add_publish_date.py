# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py add_publish_date"


# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from creation.models import TutorialResource, PublishTutorialLog


class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print('>> adding publish dates in TutorialResource')
        count = 0
        tutorials = TutorialResource.objects.filter(status__gt=0)
        for tutorial in tutorials:
            count = count + 1
            log_obj = PublishTutorialLog.objects.filter(tutorial_resource_id=tutorial.id, created__isnull=False).order_by('-id').first()
            if log_obj:
                tutorial.publish_at = log_obj.created
            else:
                tutorial.publish_at = tutorial.created
            print((tutorial.id, ':', tutorial.publish_at))
            tutorial.save()
        print(('>> Script Completed. tutorials publish date added', count))
