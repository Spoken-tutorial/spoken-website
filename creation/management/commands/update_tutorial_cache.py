from django.core.management.base import BaseCommand
from creation.models import TutorialSummaryCache, TutorialResource
from django.db.models import Q
from collections import defaultdict


class Command(BaseCommand):
    help = 'Updates the cache table with tutorial count and first tutorial for each FOSS'

    def handle(self, *args, **kwargs):
        print("Updating tutorial cache...")
        # fetch all tutorial resources sorted by foss and order
        tutorials = TutorialResource.objects.filter(Q(status=1) | Q(status=2), language__name='English').order_by(
            'tutorial_detail__foss_id', 'tutorial_detail__order'
        ).values('tutorial_detail__foss_id', 'id')

        # group & count
        summary_map = {}
        seen = set()
        for row in tutorials:
            fid = row['tutorial_detail__foss_id']
            if fid not in seen:
                seen.add(fid)
                summary_map[fid] = {
                    'count':1,
                    'first_tutorial_id': row['id']
                }
            else:
                summary_map[fid]['count'] += 1

        # store in db table
        to_create = []
        for fid, data in summary_map.items():
            to_create.append(TutorialSummaryCache(
                foss_id=fid,
                tutorial_count=data['count'],
                first_tutorial_id=data['first_tutorial_id']
            ))
        TutorialSummaryCache.objects.all().delete() # clear old cache
        TutorialSummaryCache.objects.bulk_create(to_create)

        print(f"Updated {len(to_create)} FOSS tutorial summaries.")
        




